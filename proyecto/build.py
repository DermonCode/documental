import json, os, sys, subprocess, math
import numpy as np, pyloudnorm as pyln
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from concurrent.futures import ThreadPoolExecutor
from plan import ANCHORS, MUSIC

V = int(sys.argv[1])          # 1 = clips only, 2 = clips + graphics
W, H, FPS, SR = 1280, 720, 30, 48000
TL = json.load(open('timeline.json')); IT = TL['items']; TOTAL = TL['total'] + 0.5
F = '/usr/share/fonts/opentype/inter/'
def font(n, s): return ImageFont.truetype(F + n if n.endswith('otf') else n, s)
MONO = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'

def find(sub):
    for i, it in enumerate(IT):
        if 'text' in it and sub in it['text']: return i
    raise SystemExit('anchor not found: ' + sub)

# ---------- graphics (V2) ----------
ease = lambda x: 1 - (1 - max(0, min(1, x))) ** 3
WHITE, GOLD, RED, GREY = (255, 255, 255), (255, 200, 60), (255, 80, 70), (190, 190, 200)

def ctext(d, y, txt, f, col, a=255):
    w = d.textlength(txt, font=f); d.text(((W - w) / 2, y), txt, font=f, fill=col + (a,))

def wrap(d, txt, f, maxw):
    out, cur = [], ''
    for w in txt.split():
        if d.textlength((cur + ' ' + w).strip(), font=f) > maxw: out.append(cur); cur = w
        else: cur = (cur + ' ' + w).strip()
    return out + [cur]

def g_big(t, dur, txt, sub='', col=WHITE, size=150):
    im = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(im); a = int(255 * ease(t / .35))
    f = font('InterDisplay-Black.otf', size)
    while d.textlength(txt, font=f) > W - 120: size -= 8; f = font('InterDisplay-Black.otf', size)
    ctext(d, H / 2 - size * .75 - 10 * (1 - ease(t / .35)), txt, f, col, a)
    for k, l in enumerate(wrap(d, sub, font('Inter-Medium.otf', 38), 1000)):
        ctext(d, H / 2 + size * .45 + k * 48, l, font('Inter-Medium.otf', 38), GREY, a)
    return im

def g_counter(t, dur, a0, a1, fmt, sub='', col=WHITE):
    v = a0 + (a1 - a0) * ease(t / min(1.8, dur * .7))
    return g_big(max(t, .35), dur, fmt.format(v), sub, col)

def g_quote(t, dur, txt, who):
    im = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(im); a = int(255 * ease(t / .4))
    f = font('Inter-Italic.otf', 46 if len(txt) < 140 else 38)
    ls = wrap(d, '“' + txt + '”', f, 980); lh = f.size * 1.35
    y0 = H / 2 - (len(ls) * lh + 60) / 2
    d.rectangle([130, y0, 138, y0 + len(ls) * lh], fill=GOLD + (a,))
    for k, l in enumerate(ls): d.text((170, y0 + k * lh), l, font=f, fill=WHITE + (a,))
    d.text((170, y0 + len(ls) * lh + 24), '— ' + who, font=font('Inter-Medium.otf', 32), fill=GREY + (a,))
    return im

def g_bars(t, dur, rows, unit, title, anim='last'):
    im = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(im)
    mx = max(r[1] for r in rows); fl = font('Inter-Medium.otf', 34); fv = font('InterDisplay-Bold.otf', 44)
    ctext(d, 110, title, font('Inter-Bold.otf', 40), GREY)
    y0 = H / 2 - len(rows) * 60 + 40
    for k, (lab, val) in enumerate(rows):
        p = ease(t / 1.0) if (anim == 'all' or k == len(rows) - 1) else 1
        y = y0 + k * 120; bw = 600 * val / mx * p
        d.text((120, y + 8), lab, font=fl, fill=WHITE + (255,))
        d.rectangle([400, y, 400 + bw, y + 64], fill=(RED if k == len(rows) - 1 and anim == 'last' else GOLD) + (255,))
        lab2 = (f'{val * p:.1f}'.removesuffix('.0') + '%') if '%' in unit else unit.format(val * p)
        d.text((415 + bw, y + 6), lab2, font=fv, fill=WHITE + (255,))
    return im

def g_progress(t, dur, title, sub):
    im = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(im); p = ease(t / (dur * .75))
    ctext(d, 200, title, font('Inter-Bold.otf', 52), WHITE)
    d.rectangle([190, 330, 1090, 400], outline=GREY + (255,), width=4)
    d.rectangle([198, 338, 198 + 884 * p, 392], fill=(GOLD if p < 1 else (90, 220, 120)) + (255,))
    ctext(d, 440, f'{100 * p:.1f}%', font('InterDisplay-Black.otf', 110), WHITE)
    ctext(d, 590, sub, font('Inter-Medium.otf', 34), GREY)
    return im

FUNCS = [f'func_8{0x2A100 + k * 0x1F4:06X}' for k in range(40)]
def g_terminal(t, dur, lines=None):
    im = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(im); f = font(MONO, 30)
    d.rounded_rectangle([100, 70, 1180, 650], 18, fill=(12, 14, 18, 235))
    rows = lines or [f'{fn}.c {"." * 18} MATCH ✓' for fn in FUNCS]
    n = int(t * (3.2 if not lines else len(rows) / max(1, dur * .8))) + 1
    for k, r in enumerate(rows[max(0, n - 15):n]):
        col = (90, 230, 120) if 'MATCH' in r else ((255, 200, 60) if r.startswith('>') else (220, 220, 220))
        d.text((140, 100 + k * 36), r, font=f, fill=col + (255,))
    return im

def g_list(t, dur, items, times):
    im = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(im); f = font('Inter-Bold.otf', 58)
    y0 = H / 2 - len(items) * 55
    for k, (it, tt) in enumerate(zip(items, times)):
        a = int(255 * ease((t - tt) / .3))
        if a > 0: d.text((200, y0 + k * 110), it, font=f, fill=(RED if it.startswith('×') else WHITE) + (a,))
    return im

def g_title(t, dur):
    im = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(im); a = int(255 * min(ease(t / 1.5), ease((dur - t) / 1.2)))
    ctext(d, 300, 'WHO GETS TO KEEP', font('InterDisplay-Black.otf', 92), WHITE, a)
    ctext(d, 400, 'VIDEO GAMES', font('InterDisplay-Black.otf', 92), GOLD, a)
    return im

CREDITS = ['Music by Kevin MacLeod (incompetech.com)', 'Licensed under Creative Commons: By Attribution 4.0',
           'Lightless Dawn · Interloper · Investigations · Ice Flow', 'Pixelland · Heroic Age · Wholesome · Inspired',
           '', 'Game footage and trailers © their respective owners', 'Narration: synthetic voice']
def g_credits(t, dur):
    im = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(im); a = int(255 * ease(t / 1.0))
    for k, l in enumerate(CREDITS): ctext(d, 190 + k * 52, l, font('Inter-Medium.otf', 34), WHITE if k < 2 else GREY, a)
    return im

# line substring -> (kind, args, span_lines)
G = {
 "Physical software had made up": ('big', ('3%', 'of PlayStation software sales were physical'), 1),
 "Three years earlier": ('big', ('4,000+', 'classic games studied by the Video Game History Foundation', GOLD), 1),
 "Thirteen percent.": ('counter', (0, 13, '{:.0f}%', 'still available through official means'), 1),
 "The other 87%": ('big', ('87%', 'out of print', RED), 1),
 "one petition to reverse": ('counter', (0, 200000, '{:,.0f}', 'signatures on one Change.org petition'), 1),
 "Analyst Daniel Ahmad": ('quote', ('The transition was inevitable. The backlash will be forgotten in two years.', 'Daniel Ahmad, analyst (paraphrased)'), 1),
 "replied to a post claiming": ('quote', ('Piracy is the only extant form of media preservation that exists in games right now.', 'the post Cifaldi replied to'), 1),
 "As the director of a historical": ('quote', ('As the director of a historical video game preservation institution, and someone who has dedicated his entire adult life to this cause, this is accurate.', 'Frank Cifaldi, Video Game History Foundation'), 1),
 "He added, ": ('quote', ('We have attempted to work with the industry’s trade organization to find a legal path forward, but they refuse to offer a meaningful alternative.', 'Frank Cifaldi'), 1),
 "Stop Killing Games movement collected": ('counter', (0, 1294188, '{:,.0f}', "verified signatures · European Citizens' Initiative"), 1),
 "A legal obligation to keep": ('quote', ('…would not be proportionate at this stage.', 'European Commission, June 16, 2026'), 1),
 "So the disc was going away.": ('list', (['×  Physical discs · 2028', '×  PS3 & Vita stores · 2027', '×  A law to keep games playable'],), 3),
 "It said the following.": ('shot', ('gfx/shot_psblog.png', .33, .80, 1.0, 1.55), 2),
 "It took down re3": ('shot', ('gfx/shot_re3.png', .5, .2, 1.0, 1.5), 1),
 "Super Smash Bros. Melee reached 100%": ('progress', ('Super Smash Bros. Melee', 'decompiled · decomp.dev'), 1),
 "Six years of work.": ('big', ('2020 → 2026', 'six years of work', GOLD), 1),
 "Used with AI (Claude).": ('big', ('"Used with AI (Claude)."', '', WHITE, 70), 1),
 "In a matching decompilation": ('terminal', (), 3),
 "Pick the easiest function left": ('terminal', (['> pick easiest unmatched function', '> try to match it', '> 10 failures? move on', '> repeat'],), 1),
 "He made more progress in three weeks": ('big', ('3 weeks > 3 months', 'progress with an AI loop vs. without'), 1),
 "In 2024, about 11%": ('bars', ([('2024', 10.9)], '{:.1f}%', 'New Steam releases disclosing generative AI'), 1),
 "In 2025, about 20%": ('bars', ([('2024', 10.9), ('2025', 19.9)], '{:.1f}%', 'New Steam releases disclosing generative AI'), 1),
 "By July 2026, 30.8%": ('bars', ([('2024', 10.9), ('2025', 19.9), ('2026', 30.8)], '{:.1f}%', 'New Steam releases disclosing generative AI'), 1),
 "In the week before June": ('bars', ([('2024', 10.9), ('2025', 19.9), ('2026', 30.8), ('Next Fest', 40)], '{:.0f}%', 'New Steam releases disclosing generative AI'), 1),
 "In the first quarter of 2026": ('bars', ([('Releases', 28), ('Sales', 17)], '{:.0f}%', 'AI-flagged games, Q1 2026', 'all'), 1),
 "A modder known as chasmlol": ('shot', ('gfx/shot_skycraft.png', .3, .3, 1.0, 1.4), 1),
 "The two talk to each other": ('big', ('Skyrim ⇄ Minecraft', 'connected through shared memory', WHITE, 110), 1),
 "It was a format.": ('split', (['fallout', 'outerwilds', 'gta3'],), 1),
 "had cost 315 million": ('counter', (0, 315, '${:.0f}M', "Marvel's Spider-Man 2 budget (Insomniac leak, 2023)", GOLD), 1),
 "Spider-Man 3 was planned": ('big', ('$385M', 'Spider-Man 3, planned budget', RED), 1),
 "Sandfall's CEO said": ('bars', ([("Spider-Man 2", 315), ('Clair Obscur', 10)], '${:.0f}M', 'Development budget', 'all'), 1),
 "They only have like 33": ('quote', ('They only have like 33 team members and a dog.', 'Hideo Kojima'), 1),
 "Silksong sold over 7 million": ('counter', (0, 7, '{:.0f} million', 'copies in three months', GOLD), 1),
 "together made over half a billion": ('big', ('$500M+', 'five new 2025 hits, combined', GOLD), 1),
 "Around 20,000 games launched": ('big', ('20,000 → 300', 'Steam games released in 2025 → those that made $1M+'), 1),
}
GF = {'big': g_big, 'counter': g_counter, 'quote': g_quote, 'bars': g_bars, 'progress': g_progress,
      'terminal': g_terminal, 'list': g_list, 'title': g_title, 'credits': g_credits}

# ---------- shot list ----------
anch = sorted((find(s), ks) for s, ks in ANCHORS)
clips = {f[:-4]: float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', 'clips/' + f]))
         for f in os.listdir('clips') if f.endswith('.mp4') and '.full' not in f}
bounds = [(i, it['start']) for i, it in enumerate(IT) if 'text' in it or 'pause' in it]
shots = []
for n, (i, st) in enumerate(bounds):
    en = bounds[n + 1][1] if n + 1 < len(bounds) else TOTAL
    shots.append({'i': i, 's': st, 'e': en})
gmap = {find(k): v for k, v in G.items()} if V == 2 else {}
title_i = next(i for i, it in enumerate(IT) if 'cue' in it and 'TÍTULO' in it['cue'])
merged = []; skip = 0
for n, sh in enumerate(shots):
    if skip: merged[-1]['e'] = sh['e']; merged[-1]['times'].append(sh['s'] - merged[-1]['s']); skip -= 1; continue
    sh['times'] = [0]
    if sh['i'] in gmap:
        sh['g'] = gmap[sh['i']]; skip = sh['g'][2] - 1
    elif sh['i'] == title_i + 1: sh['g'] = ('title', (), 1)
    elif n == len(shots) - 1: sh['g'] = ('credits', (), 1)
    if merged and 'g' not in sh and 'g' not in merged[-1] and sh['e'] - sh['s'] < 1.0: merged[-1]['e'] = sh['e']; continue
    merged.append(sh)
final = []
for sh in merged:
    d = sh['e'] - sh['s']; k = 1 if 'g' in sh else max(1, math.ceil(d / 6.5))
    for j in range(k): final.append(dict(sh, s=sh['s'] + d * j / k, e=sh['s'] + d * (j + 1) / k, part=j))
cursor, rot = {}, {}
for sh in final:
    a, ks = next(((a, ks) for a, ks in reversed(anch) if a <= sh['i']), anch[0])
    ks = [k for k in ks if k in clips] or ['ps5', 'pscm']; r = rot.get(a, 0); rot[a] = r + 1
    k = ks[r % len(ks)]; d = sh['e'] - sh['s']; c = cursor.get(k, max(2.0, clips[k] * .12))
    if c + d > clips[k] - 1: c = 2.0 + (c % 7)
    sh['clip'], sh['off'] = k, c; cursor[k] = c + d + 1.5
    if 'g' in sh and sh['g'][0] in ('title', 'credits') and V == 1: pass
    elif V == 1: sh.pop('g', None)

# ---------- render ----------
os.makedirs(f'seg/v{V}', exist_ok=True)
ENC = ['-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', '-r', str(FPS)]
def render(n):
    sh = final[n]; out = f'seg/v{V}/{n:04d}.mp4'
    nf = round(sh['e'] * FPS) - round(sh['s'] * FPS); dur = nf / FPS
    src = ['-ss', f"{sh['off']:.2f}", '-t', f'{dur + .5:.2f}', '-i', f"clips/{sh['clip']}.mp4"]
    g = sh.get('g')
    if not g:
        cmd = ['ffmpeg', '-v', 'error', '-y'] + src + ['-vf', f'scale={W}:{H},setsar=1', '-frames:v', str(nf)] + ENC + [out]
        return subprocess.run(cmd, check=True)
    kind, args = g[0], g[1]
    if kind == 'shot':
        png, cx, cy, z0, z1 = args
        vf = (f"scale=-2:{H * 3},zoompan=z='{z0}+({z1}-{z0})*(1-pow(1-on/{nf},3))':x='iw*{cx}-iw/zoom/2':y='ih*{cy}-ih/zoom/2':d={nf}:s={W}x{H}:fps={FPS}")
        return subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', png, '-vf', vf, '-frames:v', str(nf)] + ENC + [out], check=True)
    if kind == 'split':
        ins = []
        for k in args[0]: ins += ['-ss', '5', '-t', f'{dur + .5:.2f}', '-i', f'clips/{k}.mp4']
        fc = ';'.join(f'[{j}:v]scale=-2:{H},crop={W // 3}:{H}[c{j}]' for j in range(3)) + f';[c0][c1][c2]hstack=3,pad={W}:{H}:(ow-iw)/2:0'
        return subprocess.run(['ffmpeg', '-v', 'error', '-y'] + ins + ['-filter_complex', fc, '-frames:v', str(nf)] + ENC + [out], check=True)
    bg = 'boxblur=14:2,eq=brightness=-0.32' if kind not in ('title', 'credits') else 'eq=brightness=-0.25'
    cmd = ['ffmpeg', '-v', 'error', '-y'] + src + ['-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
           '-filter_complex', f'[0:v]scale={W}:{H},setsar=1,{bg}[b];[b][1:v]overlay', '-frames:v', str(nf)] + ENC + [out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    extra = (sh['times'],) if kind == 'list' else ()
    for f in range(nf): p.stdin.write(GF[kind](f / FPS, dur, *args, *extra).tobytes())
    p.stdin.close(); p.wait()

with ThreadPoolExecutor(4) as ex: list(ex.map(render, range(len(final))))
with open(f'seg/v{V}/list.txt', 'w') as f: f.writelines(f"file '{n:04d}.mp4'\n" for n in range(len(final)))
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-i', f'seg/v{V}/list.txt', '-c', 'copy', f'video_v{V}.mp4'], check=True)

# ---------- audio (shared) ----------
if not os.path.exists('mix.wav'):
    def dec(f): return np.frombuffer(subprocess.check_output(['ffmpeg', '-v', 'error', '-i', f, '-f', 'f32le', '-ac', '2', '-ar', str(SR), '-']), np.float32).reshape(-1, 2)
    meter = pyln.Meter(SR); N = (int(TOTAL) + 2) * SR
    nar = np.zeros((N, 2), np.float32)
    for i, it in enumerate(IT):
        if 'text' in it: a = dec(f'tts/{i:03d}.mp3'); s = int(it['start'] * SR); nar[s:s + len(a)] += a[:N - s]
    nar = pyln.normalize.loudness(nar, meter.integrated_loudness(nar), -16)
    mus = np.zeros_like(nar); ms = sorted((IT[find(s)]['start'], t) for s, t in MUSIC)
    for k, (st, tr) in enumerate(ms):
        en = ms[k + 1][0] if k + 1 < len(ms) else TOTAL
        a = dec(f'music/{tr}.mp3'); a = pyln.normalize.loudness(a, meter.integrated_loudness(a), -16)
        s0 = max(0, int((st - .75) * SR)); L = int((en + .75) * SR) - s0
        a = np.tile(a, (L // len(a) + 1, 1))[:L].copy(); fi, fo = int(1.5 * SR), int(2.0 * SR)
        a[:fi] *= np.linspace(0, 1, fi)[:, None]; a[-fo:] *= np.linspace(1, 0, fo)[:, None]
        mus[s0:s0 + L] += a[:N - s0]
    hop = SR // 100; env = np.abs(nar[:, 0]).reshape(-1, hop).max(1) > 0.01
    act = np.convolve(env.astype(float), np.ones(45), 'same') > 0          # hold ~0.45 s
    gain = np.where(act, 10 ** (-17 / 20), 10 ** (-7 / 20))
    gain = np.convolve(gain, np.ones(25) / 25, 'same')                     # smooth ~0.25 s
    mix = nar + mus * np.repeat(gain, hop)[:, None]
    mix = pyln.normalize.loudness(mix, meter.integrated_loudness(mix), -14)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ac', '2', '-ar', str(SR), '-i', '-', '-af', 'alimiter=limit=0.89:level=false', 'mix.wav'],
                   input=mix.astype(np.float32).tobytes(), check=True)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'video_v{V}.mp4', '-i', 'mix.wav', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest',
                '-movflags', '+faststart', f'documental_v{V}.mp4'], check=True)
print('done', V, len(final), 'shots', f'{TOTAL:.1f}s')

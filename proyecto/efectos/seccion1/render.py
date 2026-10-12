import os, sys, math, subprocess, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
cv2.setNumThreads(1)
W, H, FPS = 1920, 1080, 30
END = 61.844; NF = int(round(END * FPS))
D = os.path.dirname(os.path.abspath(__file__))
FD = 'C:/Windows/Fonts/'; LIGHT, SEMI, BOLD = FD + 'segoeuil.ttf', FD + 'segoeuisl.ttf', FD + 'segoeuib.ttf'
BLOG = os.path.join(D, '..', '..', 'gfx', 'shot_psblog.png')

def cl(x, a=0., b=1.): return max(a, min(b, x))
def eo(x): x = cl(x); return 1 - (1 - x) ** 3
def eio(x): x = cl(x); return x * x * (3 - 2 * x)
def lerp(a, b, x): return a + (b - a) * x
def seg(t, a, b): return cl((t - a) / (b - a))
def bump(t, a, b): return math.sin(math.pi * seg(t, a, b)) if a < t < b else 0.

# ---------------- footage ----------------
class Clip:
    def __init__(s, name): s.cap = cv2.VideoCapture(f'{D}/clips/{name}.mp4'); s.pos = -10; s.cache = {}
    def idx(s, i):
        i = max(0, i)
        if i in s.cache: return s.cache[i]
        if i != s.pos + 1: s.cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        ok, f = s.cap.read()
        if not ok: return s.cache[max(s.cache)] if s.cache else np.zeros((H, W, 3), np.float32)
        s.pos = i; f = f[:, :, ::-1].astype(np.float32) / 255
        s.cache = {k: v for k, v in s.cache.items() if k >= i - 2}; s.cache[i] = f
        return f
    def at(s, ct, blend=False):
        x = ct * FPS
        if not blend: return s.idx(int(round(x)))
        i = int(math.floor(x)); a = x - i
        f0 = s.idx(i)
        return f0 if a < 0.02 else f0 * (1 - a) + s.idx(i + 1) * a
CLIPS = {}
def clip(name, slot=0):
    k = (name, slot)
    if k not in CLIPS: CLIPS[k] = Clip(name)
    return CLIPS[k]

LW = np.array([0.2126, 0.7152, 0.0722], np.float32)
def grade(f, bright=1.0):
    l = (f @ LW)[..., None]
    f = l + (f - l) * 0.84
    f = np.clip(f, 0, 1); f = f * f * (3 - 2 * f) * 0.4 + f * 0.6
    f = f * np.array([0.95, 0.975, 1.0], np.float32) + (1 - l) * np.array([0, 0.004, 0.01], np.float32)
    return f * (0.93 * bright)

def foot(name, ct, zoom=1.0, cx=0.5, cy=0.5, slot=0, blend=False, size=(W, H)):
    f = clip(name, slot).at(max(0, ct), blend)
    cw, ch = W / zoom, H / zoom
    x0 = cl(cx * W - cw / 2, 0, W - cw); y0 = cl(cy * H - ch / 2, 0, H - ch)
    M = np.float32([[size[0] / cw, 0, -x0 * size[0] / cw], [0, size[1] / ch, -y0 * size[1] / ch]])
    return grade(cv2.warpAffine(f, M, size, flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT))

def crop(name, ct, box, size, slot=0):
    f = clip(name, slot).at(max(0, ct)); x, y, w, h = box
    return grade(cv2.resize(f[y:y + h, x:x + w], size, interpolation=cv2.INTER_AREA))

# ---------------- background: smoke + dust ----------------
def fbm(h, w, seed, octs=(3, 5, 9, 17, 33, 65), pers=0.55):
    r = np.random.default_rng(seed); out = np.zeros((h, w), np.float32); amp, tot = 1., 0.
    for o in octs:
        g = r.random((max(2, int(o * h / w)) + 1, o + 1)).astype(np.float32)
        out += amp * cv2.resize(g, (w, h), interpolation=cv2.INTER_CUBIC); tot += amp; amp *= pers
    return out / tot
SW, SH = 1500, 860
def ridged(n): n = (n - n.min()) / (n.max() - n.min()); return (1 - np.abs(2 * n - 1)) ** 3
L1 = ridged(fbm(SH, SW, 1)); L2 = ridged(fbm(SH, SW, 2)); L3 = fbm(SH, SW, 3)
yy, xx = np.mgrid[0:540, 0:960].astype(np.float32)
LIGHTMAP = np.exp(-(((xx - 480) / 620) ** 2 + ((yy - 200) / 420) ** 2)).astype(np.float32)
def make_stars(seed, n, w, h):
    r = np.random.default_rng(seed); s = np.zeros((h, w), np.float32)
    for _ in range(n):
        x, y = r.integers(0, w), r.integers(0, h); s[y, x] = r.uniform(0.3, 1.0) * (3 if r.random() < 0.08 else 1)
    return cv2.GaussianBlur(s, (0, 0), 1.1) * 4
STARS = make_stars(7, 1400, 2300, 1300)
SMOKE_COL = np.array([0.93, 0.96, 1.0], np.float32)
def smoke(t, k=1.0):
    a = L1[int(130 + t * 2.2):, int(60 + t * 5.5):][:540, :960]
    b = L2[int(250 - t * 1.6):, int(480 - t * 4.0):][:540, :960]
    c = L3[int(100 + t * 1.0):, int(200 + t * 2.0):][:540, :960]
    s = (0.55 * a + 0.45 * b) * (0.55 + 0.9 * c)
    s = (0.012 + s * 0.17 * (0.35 + 0.9 * LIGHTMAP)) * k
    s = cv2.resize(s, (W, H), interpolation=cv2.INTER_LINEAR)
    st = STARS[int(80 + t * 1.5):, int(100 + t * 3.0):][:H, :W] * 0.11 * k
    return (s + st)[..., None] * SMOKE_COL

# ---------------- 3D quads ----------------
FL = 1600.
def rot(rx, ry, rz):
    a, b, c = map(math.radians, (rx, ry, rz))
    Rx = np.array([[1, 0, 0], [0, math.cos(a), -math.sin(a)], [0, math.sin(a), math.cos(a)]])
    Ry = np.array([[math.cos(b), 0, math.sin(b)], [0, 1, 0], [-math.sin(b), 0, math.cos(b)]])
    Rz = np.array([[math.cos(c), -math.sin(c), 0], [math.sin(c), math.cos(c), 0], [0, 0, 1]])
    return Rx @ Ry @ Rz
def quad(w, h, cx, cy, z, rx=0, ry=0, rz=0):
    p = np.array([[-w / 2, -h / 2, 0], [w / 2, -h / 2, 0], [w / 2, h / 2, 0], [-w / 2, h / 2, 0]]) @ rot(rx, ry, rz).T
    p += [cx - W / 2, cy - H / 2, z]
    s = FL / (FL + p[:, 2]); return np.float32(np.stack([W / 2 + p[:, 0] * s, H / 2 + p[:, 1] * s], 1))
def homog(img_wh, dst):
    w, h = img_wh; return cv2.getPerspectiveTransform(np.float32([[0, 0], [w, 0], [w, h], [0, h]]), dst)
def warp_to(img, dst, frame, additive=False):
    h, w = img.shape[:2]
    x0 = int(max(0, math.floor(dst[:, 0].min()))); x1 = int(min(W, math.ceil(dst[:, 0].max()) + 1))
    y0 = int(max(0, math.floor(dst[:, 1].min()))); y1 = int(min(H, math.ceil(dst[:, 1].max()) + 1))
    if x1 <= x0 or y1 <= y0: return
    M = homog((w, h), dst - np.float32([x0, y0]))
    p = cv2.warpPerspective(img, M, (x1 - x0, y1 - y0), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    reg = frame[y0:y1, x0:x1]
    if additive: reg += p
    else: a = p[..., 3:4]; reg *= (1 - a); reg += p[..., :3]

def rrect(w, h, r, s=4):
    m = np.zeros((h * s, w * s), np.uint8); r *= s
    cv2.rectangle(m, (r, 0), (w * s - r, h * s), 255, -1); cv2.rectangle(m, (0, r), (w * s, h * s - r), 255, -1)
    for cx, cy in ((r, r), (w * s - r, r), (r, h * s - r), (w * s - r, h * s - r)): cv2.circle(m, (cx, cy), r, 255, -1)
    return cv2.resize(m, (w, h), interpolation=cv2.INTER_AREA).astype(np.float32) / 255

# ---------------- text ----------------
_fonts, _tc = {}, {}
def font(p, s):
    if (p, s) not in _fonts: _fonts[(p, s)] = ImageFont.truetype(p, s)
    return _fonts[(p, s)]
def text_img(txt, fp, size, track=0.):
    k = (txt, fp, size, track)
    if k in _tc: return _tc[k]
    f = font(fp, size); adv = [f.getlength(c) for c in txt]
    tw = sum(adv) + track * size * (len(txt) - 1); asc, desc = f.getmetrics(); pad = int(size * 0.7)
    im = Image.new('L', (int(math.ceil(tw)) + 2 * pad, asc + desc + 2 * pad), 0); d = ImageDraw.Draw(im); x = pad
    for c, a in zip(txt, adv): d.text((x, pad), c, font=f, fill=255); x += a + track * size
    r = np.asarray(im, np.float32) / 255; _tc[k] = r; return r
def put(frame, a, cx, cy, color=(1, 1, 1), op=1., blur=0., scale=1., glow=0.45):
    if op <= 0.003: return
    if abs(scale - 1) > 1e-3: a = cv2.resize(a, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)
    if blur > 0.35: a = cv2.GaussianBlur(a, (0, 0), blur)
    h, w = a.shape; x0 = int(round(cx - w / 2)); y0 = int(round(cy - h / 2))
    ax0, ay0 = max(0, -x0), max(0, -y0); ax1, ay1 = min(w, W - x0), min(h, H - y0)
    if ax1 <= ax0 or ay1 <= ay0: return
    A = a[ay0:ay1, ax0:ax1] * op; reg = frame[y0 + ay0:y0 + ay1, x0 + ax0:x0 + ax1]
    col = np.array(color, np.float32)
    reg *= (1 - A[..., None]); reg += A[..., None] * col
    if glow > 0:
        g = cv2.GaussianBlur(A, (0, 0), max(5., h * 0.07)); reg += g[..., None] * col * glow
def txt(frame, s, fp, size, cx, cy, track=0., **kw): put(frame, text_img(s, fp, size, track), cx, cy, **kw)
def textw(s, fp, size, track=0.):
    f = font(fp, size); return sum(f.getlength(c) for c in s) + track * size * (len(s) - 1)
def reveal(frame, t, t0, s, fp, size, cx, cy, track=0., t_out=None, dur=0.7, color=(1, 1, 1), glow=0.45, rise=14):
    p = eo(seg(t, t0, t0 + dur)); op = p; blur = (1 - p) * 12; dy = (1 - p) * rise; sc = 1 + (1 - p) * 0.06
    if t_out is not None:
        q = eio(seg(t, t_out, t_out + 0.45)); op *= 1 - q; blur += q * 14; sc += q * 0.05
    txt(frame, s, fp, size, cx, cy + dy, track, op=op, blur=blur, scale=sc, color=color, glow=glow)

# ---------------- B/C: three floating cards ----------------
CW, CH, CM = 500, 312, 40
CMASK = rrect(CW, CH, 16)
_o = rrect(CW + 8, CH + 8, 20); _i = np.pad(rrect(CW + 2, CH + 2, 17), 3)
STROKE = np.pad(np.clip(_o - _i, 0, 1), CM - 4)
CGLOW = cv2.GaussianBlur(STROKE, (0, 0), 7) * 2.6 + cv2.GaussianBlur(STROKE, (0, 0), 22) * 1.4
NEON = np.array([0.80, 0.92, 1.0], np.float32)
CARDS = [
    dict(clip='shelf', ct0=30.0, rate=1.0, box=(240, 90, 1440, 900), label='CARTRIDGE', tin=4.96, x=420, y=520, ry=17, ph=0.0),
    dict(clip='mpdisc', ct0=0.5, rate=1.0, box=(300, 130, 1320, 825), label='DISC', tin=5.98, x=960, y=560, ry=0, ph=0.37),
    dict(clip='mpbox', ct0=35.6, rate=0.8, box=(290, 140, 1340, 838), label='BOX', tin=6.83, x=1500, y=520, ry=-17, ph=0.71),
]
FLICK = [1, .3, .95, .12, .7, .05, 0]
def neon_level(t, toff):
    if t < toff: return 1.
    i = int((t - toff) / 0.05); return FLICK[i] if i < len(FLICK) else 0.
def shot_B(t):
    fr = smoke(t)
    foc = eio(seg(t, 7.3, 9.6))
    items = []
    for k, c in enumerate(CARDS):
        if t < c['tin']: continue
        e = eo(seg(t, c['tin'], c['tin'] + 0.85)); op = cl(seg(t, c['tin'], c['tin'] + 0.4))
        z = lerp(1100, 0, e); blur = (1 - e) * 9; sgn = 1 if k < 2 else -1
        ph = c['ph'] * 6.283
        x, y = c['x'], c['y'] + (1 - e) * 60 + 9 * math.sin(t * 1.1 + ph)
        ry = c['ry'] + (1 - e) * 28 * sgn + 2.5 * math.sin(t * 0.8 + ph); rx = 4 * math.sin(t * 0.7 + ph * 1.3) + (1 - e) * 10
        rz = 1.5 * math.sin(t * 0.6 + ph)
        if k < 2: z += 380 * foc; blur += 5.5 * foc; op *= 1 - 0.45 * foc; x = lerp(x, x - 140, foc)
        else: x = lerp(x, 1180, foc); y = lerp(y, 540, foc); z -= 330 * foc; ry = lerp(ry, -7, foc)
        toff = 10.22 + 0.27 * k; nl = neon_level(t, toff)
        dim = 1 - 0.72 * eio(seg(t, toff + 0.1, toff + 0.45))
        land = bump(t, c['tin'] + 0.45, c['tin'] + 1.1)
        items.append((z, k, c, x, y, rx, ry, rz, op, blur, nl * (1 + 1.6 * land), dim, e))
    for z, k, c, x, y, rx, ry, rz, op, blur, nl, dim, e in sorted(items, key=lambda i: -i[0]):
        ct = c['ct0'] + (t - c['tin']) * c['rate']
        img = crop(c['clip'], ct, c['box'], (CW, CH)) * dim
        rgba = np.zeros((CH + 2 * CM, CW + 2 * CM, 4), np.float32)
        rgba[CM:CM + CH, CM:CM + CW, :3] = img * CMASK[..., None] * op
        rgba[CM:CM + CH, CM:CM + CW, 3] = CMASK * op
        if blur > 0.4: rgba = cv2.GaussianBlur(rgba, (0, 0), blur)
        dst = quad(CW + 2 * CM, CH + 2 * CM, x, y, z, rx, ry, rz)
        warp_to(rgba, dst, fr)
        if nl > 0.01:
            em = ((STROKE + CGLOW) * nl * op)[..., None] * NEON
            if blur > 0.4: em = cv2.GaussianBlur(em, (0, 0), blur)
            warp_to(em, dst, fr, additive=True)
        bx = float(dst[2:, 0].mean()); by = float(dst[2:, 1].max()) + 8
        lp = eo(seg(t, c['tin'] + 0.25, c['tin'] + 0.95))
        txt(fr, c['label'], SEMI, 30, bx, by + (1 - lp) * 10, 0.42, op=op * lp * (0.35 + 0.65 * nl if t > 10.2 else 1) * dim,
            blur=(1 - lp) * 8 + blur * 0.6, color=(0.86, 0.9, 0.96), glow=0.35)
    return crt_off(fr, t)
def crt_off(fr, t):
    if t < 11.30: return fr
    if t > 12.12: return np.zeros_like(fr)
    p1 = eo(seg(t, 11.30, 11.58)); p2 = eio(seg(t, 11.60, 11.86)); p3 = seg(t, 11.86, 12.12)
    sy = max(lerp(1, 0.0035, p1), 2 / H); sx = max(lerp(1, 0.003, p2), 3 / W)
    g = 1 + 3.5 * p1
    w_, h_ = max(3, int(W * sx)), max(2, int(H * sy))
    small = cv2.resize(fr, (w_, h_), interpolation=cv2.INTER_AREA) * g
    wm = seg(p1, 0.75, 1.0)
    if wm > 0: small = small * (1 - wm) + np.full_like(small, 0.95) * wm
    out = np.zeros_like(fr); x0, y0 = (W - w_) // 2, (H - h_) // 2
    out[y0:y0 + h_, x0:x0 + w_] = small
    out += cv2.GaussianBlur(out, (0, 0), 14) * (0.8 * p1)
    return out * (1 - p3)
def crt_on(fr, t, t0):
    if t >= t0 + 0.42: return fr
    p1 = eo(seg(t, t0 + 0.04, t0 + 0.16)); p2 = eo(seg(t, t0 + 0.16, t0 + 0.42))
    sx = max(p1, 3 / W); sy = max(p2, 2 / H); g = 1 + 3 * (1 - p2)
    w_, h_ = max(3, int(W * sx)), max(2, int(H * sy))
    small = cv2.resize(fr, (w_, h_), interpolation=cv2.INTER_AREA) * g
    if p2 < 0.5: small = small * p2 * 2 + np.full_like(small, 0.9) * (1 - p2 * 2)
    out = np.zeros_like(fr); x0, y0 = (W - w_) // 2, (H - h_) // 2
    out[y0:y0 + h_, x0:x0 + w_] = small
    out += cv2.GaussianBlur(out, (0, 0), 14) * 0.8 * (1 - p2)
    return out * cl(seg(t, t0, t0 + 0.05))

# ---------------- D: PlayStation Blog page ----------------
_pg = cv2.imread(BLOG)[45:1500, 40:1720, ::-1].astype(np.float32) / 255 * 0.9
PH_, PW_ = _pg.shape[:2]
PAGE = _pg; PAGEB = cv2.GaussianBlur(_pg, (0, 0), 3)
PAGE_SH = np.pad(np.ones((PH_, PW_), np.float32), 80); PAGE_SH = cv2.GaussianBlur(PAGE_SH, (0, 0), 35)
PY = np.arange(PH_, dtype=np.float32)[:, None]; PX = np.arange(PW_, dtype=np.float32)[None, :]
HEAD, PARA, JAN = (700, 645), (800, 1170), (1385, 1168)
WS = 0.9
PLATE = np.pad(rrect(424, 100, 22), ((8, 8), (8, 8)))
def page_geom(t):
    k = eio(seg(t, 13.4, 20.4))
    e = eo(seg(t, 13.55, 14.75))
    f1 = eio(seg(t, 14.6, 17.0)); f2 = eio(seg(t, 17.2, 18.9))
    fx = lerp(lerp(HEAD[0], PARA[0], f1), JAN[0], f2); fy = lerp(lerp(HEAD[1], PARA[1], f1), JAN[1], f2)
    ry = lerp(lerp(-17, -9, k), -3, f1) - (1 - e) * 20; rx = lerp(lerp(13, 7, k), 2.5, f1) + (1 - e) * 15; rz = lerp(lerp(-2.5, -1, k), 0, f1)
    z = lerp(250, -120, k) - 580 * f1 - 80 * f2 + (1 - e) * 2600
    tx, ty = W / 2 + 40, H / 2 + 30
    cx, cy = W / 2, H / 2
    for _ in range(3):
        dst = quad(PW_ * WS, PH_ * WS, cx, cy, z, rx, ry, rz)
        p = homog((PW_, PH_), dst) @ np.array([fx, fy, 1.]); px, py = p[0] / p[2], p[1] / p[2]
        sc = FL / (FL + z); cx += (tx - px) / sc; cy += (ty - py) / sc
    return quad(PW_ * WS, PH_ * WS, cx, cy, z, rx, ry, rz), fy, e
def shot_D(t):
    fr = smoke(t)
    hq = eio(seg(t, 13.4, 14.0)); ho = 1 - eio(seg(t, 18.75, 19.15))
    def hdr(fr):
        if ho <= 0: return
        if hq > 0:  # frosted dark plate behind the header
            k_ = hq * ho; x0, y0 = W // 2 - 220, 29
            roi = fr[y0:y0 + 116, x0:x0 + 440]; m_ = cv2.GaussianBlur(PLATE, (0, 0), 2)[..., None] * k_
            fr[y0:y0 + 116, x0:x0 + 440] = roi * (1 - m_) + cv2.GaussianBlur(roi, (0, 0), 10) * 0.16 * m_
        for s_, fp, sz, tr, t0, y0, y1, s1, col, gl in (('JULY 1ST, 2026', LIGHT, 92, 0.2, 12.62, H / 2 - 10, 62, 0.4, (1, 1, 1), 0.5),
                                                      ('PLAYSTATION BLOG', SEMI, 26, 0.5, 12.85, H / 2 + 72, 108, 0.9, (0.7, 0.76, 0.85), 0.3)):
            p = eo(seg(t, t0, t0 + 0.7))
            txt(fr, s_, fp, sz, W / 2, lerp(y0 + (1 - p) * 14, y1, hq), tr, op=p * ho, blur=(1 - p) * 12 + (1 - ho) * 10,
                scale=lerp(1 + (1 - p) * 0.06, s1, hq), color=col, glow=gl)
    if t <= 13.5: hdr(fr)
    if t > 13.5:
        dst, fy, e = page_geom(t)
        m = np.clip(np.abs(PY - fy) / 700 - 0.3, 0, 1) ** 1.5
        pg = PAGE * (1 - m[..., None]) + PAGEB * m[..., None]
        pg = pg * (1 - 0.25 * m[..., None])
        hs = seg(t, 16.55, 17.45)
        if hs > 0:
            band = np.clip(1.6 - np.abs(PY - 1171) / 14, 0, 1) * np.clip((86 + hs * 1410 - PX) / 40, 0, 1) * (PX < 1492)
            pg = pg * (1 - 0.42 * eio(seg(t, 16.55, 16.9)) * (1 - band))[..., None]
        lift = eio(seg(t, 18.95, 19.6))
        pg = pg * (1 - 0.62 * lift)
        if lift > 0.01: pg = cv2.GaussianBlur(pg, (0, 0), 0.1 + 4 * lift)
        op = cl(seg(t, 13.55, 14.1))
        rgba = np.dstack([pg * op, np.full((PH_, PW_), op, np.float32)])
        # soft shadow under the page
        Hm = homog((PW_, PH_), dst)
        cs = np.float32([[-80, -80, 1], [PW_ + 80, -80, 1], [PW_ + 80, PH_ + 80, 1], [-80, PH_ + 80, 1]]) @ Hm.T
        sdst = np.float32(cs[:, :2] / cs[:, 2:]) + np.float32([18, 30])
        sh = np.dstack([np.zeros((PAGE_SH.shape[0], PAGE_SH.shape[1], 3), np.float32), PAGE_SH * 0.7 * op])
        warp_to(sh, sdst, fr)
        warp_to(rgba, dst, fr)
        if lift > 0:
            p = Hm @ np.array([JAN[0], JAN[1], 1.]); sx, sy = p[0] / p[2], p[1] / p[2]
            q = eo(seg(t, 18.95, 19.75))
            cx, cy = lerp(sx, W / 2, q), lerp(sy, H / 2 - 20, q)
            put(fr, text_img('JANUARY 2028', SEMI, 132, 0.14), cx, cy, op=cl(lift * 2), scale=lerp(0.22, 1.0, q),
                blur=(1 - q) * 3, glow=0.55)
            ul = eo(seg(t, 19.45, 20.1))
            if ul > 0:
                w_ = int(textw('JANUARY 2028', SEMI, 132, 0.14) * ul); y_ = int(cy + 95)
                line = np.zeros((40, max(2, w_)), np.float32); line[19:21] = 1
                put(fr, line, W / 2, y_, color=(1, 0.42, 0.38), glow=1.2)
            reveal(fr, t, 19.4, 'NO MORE NEW PLAYSTATION GAMES ON DISC', SEMI, 30, W / 2, cy + 150, 0.42, color=(0.75, 0.79, 0.86), glow=0.3)
        hdr(fr)
    return crt_on(fr, t, 12.43)

# ---------------- F/H: wall of 4,000 games ----------------
COLS, ROWS, P, TS = 100, 40, 22, 12
rng = np.random.default_rng(11)
gy, gx = np.mgrid[0:ROWS, 0:COLS]
dist = np.hypot((gx - COLS / 2) / COLS, (gy - ROWS / 2) / COLS * 1.0)
RANK = np.argsort(np.argsort((dist / dist.max() * 0.75 + rng.random((ROWS, COLS)) * 0.25).ravel())).reshape(ROWS, COLS)
KEEP = np.zeros(ROWS * COLS, bool); KEEP[rng.choice(ROWS * COLS, 520, replace=False)] = True; KEEP = KEEP.reshape(ROWS, COLS)
U = rng.random((ROWS, COLS)); U2 = rng.random((ROWS, COLS))
VX = rng.normal(0, 160, (ROWS, COLS)); VY = rng.uniform(-260, 60, (ROWS, COLS)); GZ = rng.uniform(1500, 2600, (ROWS, COLS))
_tm = np.zeros((P, P), np.float32); _tm[5:5 + TS, 5:5 + TS] = rrect(TS, TS, 3)
TMASK = np.tile(_tm, (ROWS, COLS))
_ey = np.minimum(np.arange(ROWS * P), ROWS * P - 1 - np.arange(ROWS * P)) / (ROWS * P * 0.22)
_ex = np.minimum(np.arange(COLS * P), COLS * P - 1 - np.arange(COLS * P)) / (COLS * P * 0.16)
EDGE = (np.clip(_ey, 0, 1)[:, None] * np.clip(_ex, 0, 1)[None, :]).astype(np.float32) ** 1.5
TBR = rng.uniform(0.32, 0.62, (ROWS, COLS, 1)).astype(np.float32)
LIT = np.array([0.72, 0.84, 1.0], np.float32); DIM = np.array([0.045, 0.05, 0.065], np.float32)
REDD = np.array([0.26, 0.04, 0.04], np.float32); REDB = np.array([0.62, 0.11, 0.09], np.float32); KEEPC = np.array([0.95, 0.97, 1.0], np.float32)
def lit_time(r): return 25.6 + 5.0 * (1 - (1 - r / 4000) ** (1 / 3))
LT = lit_time(RANK)
RT = 37.05 + 0.75 * (gx / COLS) * 0.7 + 0.75 * 0.3 * U
GT = 41.56 + 0.32 * U2
def wall_colors(t):
    b = np.clip((t - LT[..., None]) / 0.3, 0, 1); flash = np.clip(1 - np.abs(t - LT[..., None] - 0.18) / 0.18, 0, 1)
    c = DIM * (1 - b) + LIT * TBR * b * (1 + 1.2 * flash)
    if t > 37.0:
        r = np.clip((t - RT[..., None]) / 0.3, 0, 1)
        hot = REDD + (REDB - REDD) * eio(seg(t, 39.3, 40.4))
        c = np.where(KEEP[..., None], c * (1 - r) + KEEPC * r, c * (1 - r) + hot * r)
    return c.astype(np.float32)
def wall_cam(t):
    if t < 34:
        k = eio(seg(t, 25.32, 31.8))
        return dict(rx=lerp(38, 17, k), ry=lerp(-10, 5, k), rz=lerp(-5, -1.5, k), z=lerp(-950, 380, k), cy=lerp(560, 620, k))
    k = eio(seg(t, 35.3, 42.7))
    return dict(rx=lerp(17, 12, k), ry=lerp(5, -5, k), rz=lerp(-1.5, 1, k), z=lerp(420, 120, k), cy=630)
def draw_wall(fr, t, alpha=1.0):
    c = wall_colors(t)
    gone = np.zeros((ROWS, COLS), bool)
    if t > 41.56: gone = (~KEEP) & (t > GT)
    c2 = c.copy(); c2[gone] = 0
    img = cv2.resize(c2, (COLS * P, ROWS * P), interpolation=cv2.INTER_NEAREST) * TMASK[..., None]
    a = TMASK * EDGE * 0.92 * cv2.resize((~gone).astype(np.float32), (COLS * P, ROWS * P), interpolation=cv2.INTER_NEAREST)
    rgba = np.dstack([img * (EDGE * alpha)[..., None], a * alpha])
    if gone.any():
        for r_, c_ in zip(*np.nonzero(gone)):
            dt = t - GT[r_, c_]; fa = 1 - dt / 0.65
            if fa <= 0: continue
            x = c_ * P + 3 + VX[r_, c_] * dt; y = r_ * P + 3 + VY[r_, c_] * dt + 0.5 * GZ[r_, c_] * dt * dt
            col = REDB * (1 + 1.2 * (1 - fa)); s_ = TS * (0.6 + 0.4 * fa)
            cv2.rectangle(rgba, (int(x), int(y)), (int(x + s_), int(y + s_)),
                          (float(col[0] * fa * alpha), float(col[1] * fa * alpha), float(col[2] * fa * alpha), float(fa * alpha)), -1)
    cam = wall_cam(t)
    dst = quad(COLS * P, ROWS * P, W / 2, cam['cy'], cam['z'], cam['rx'], cam['ry'], cam['rz'])
    warp_to(rgba, dst, fr)
    gl = cv2.resize(rgba[..., :3], (COLS * P // 4, ROWS * P // 4), interpolation=cv2.INTER_AREA)
    gl = cv2.GaussianBlur(gl, (0, 0), 2.0) * 0.55 + cv2.GaussianBlur(gl, (0, 0), 7) * 0.4
    warp_to(gl, dst, fr, additive=True)
VIG = None
def text_backdrop(fr, op, cy=480):
    global VIG
    if VIG is None:
        y, x = np.mgrid[0:H, 0:W].astype(np.float32)
        VIG = np.exp(-(((x - W / 2) / 760) ** 2 + ((y - cy) / 230) ** 2))[..., None].astype(np.float32)
    fr *= 1 - 0.85 * VIG * op
def counter(fr, t, t0, t1, n_to, fmt, cx, cy, size, color, op=1., blur=0., scale=1., glow=0.5, suffix='', suf_t=None):
    n = round(n_to * eo(seg(t, t0, t1)))
    full = fmt.format(n_to); s = fmt.format(n)
    fw = textw(full, LIGHT, size, 0.04) * scale; xr = cx - textw(full + suffix, LIGHT, size, 0.04) * scale / 2 + fw
    a = text_img(s, LIGHT, size, 0.04)
    put(fr, a, xr - textw(s, LIGHT, size, 0.04) * scale / 2, cy, color, op, blur, scale, glow)
    if suffix and suf_t is not None:
        p = eo(seg(t, suf_t, suf_t + 0.4))
        sw = textw(suffix, LIGHT, size, 0.04) * scale
        put(fr, text_img(suffix, LIGHT, size, 0.04), xr + size * 0.04 * scale + sw / 2, cy, color, op * p, blur + (1 - p) * 8,
            scale * (1 + (1 - p) * 0.3), glow)
def shot_F(t):
    fr = smoke(t, 0.8); draw_wall(fr, t)
    ap = eo(seg(t, 25.45, 26.2)); out = eio(seg(t, 33.2, 33.62)); op = ap * (1 - out)
    text_backdrop(fr, op)
    counter(fr, t, 25.6, 30.6, 4000, '{:,}', W / 2, 450, 230, (1, 1, 1), op, (1 - ap) * 10 + out * 12, 1 + out * 0.05, 0.5, '+', 30.55)
    reveal(fr, t, 26.1, 'CLASSIC GAMES STUDIED BY THE VIDEO GAME HISTORY FOUNDATION', SEMI, 34, W / 2, 596, 0.3, t_out=33.2,
           color=(0.76, 0.8, 0.88), glow=0.3)
    return fr
def shot_H(t):
    fr = smoke(t, 0.8)
    fade = eo(seg(t, 35.4, 35.9))
    draw_wall(fr, t, 1.0)
    fl = math.exp(-(t - 41.56) / 0.13) * 0.22 if t > 41.56 else 0.
    if t > 36.9:
        up = eio(seg(t, 39.28, 39.8)); g13 = 1 - eio(seg(t, 42.25, 42.6))
        text_backdrop(fr, eo(seg(t, 36.95, 37.4)) * (1 - 0.4 * seg(t, 41.6, 42.4)))
        p = eo(seg(t, 37.0, 37.5))
        counter(fr, t, 37.05, 37.75, 13, '{:d}', W / 2, lerp(450, 215, up), 230, (1, 1, 1), p * lerp(1, 0.8, up) * g13,
                (1 - p) * 10, lerp(1, 0.48, up), 0.5, '%', 37.0)
        reveal(fr, t, 37.3, 'STILL AVAILABLE THROUGH OFFICIAL MEANS', SEMI, 34, W / 2, lerp(596, 300, up), 0.3, t_out=42.25,
               color=(0.76, 0.8, 0.88), glow=0.3, rise=14 * (1 - up))
        if t > 39.3:
            p = eo(seg(t, 39.32, 39.95)); d = eio(seg(t, 41.6, 42.15))
            txt(fr, '87%', LIGHT, 230, W / 2, 470 + (1 - p) * 16, 0.04, color=(1.0, 0.33, 0.30), op=p * (1 - d),
                blur=(1 - p) * 12 + d * 22, scale=1 + (1 - p) * 0.06 + d * 0.18, glow=0.65)
            reveal(fr, t, 39.6, 'OUT OF PRINT', SEMI, 34, W / 2, 610, 0.42, t_out=41.75, color=(0.9, 0.62, 0.6), glow=0.3)
    return fr + fl
# ---------------- footage shots ----------------
def vignette_extra(fr, k):
    y, x = np.ogrid[0:H, 0:W]; r = np.hypot((x - W / 2) / (W / 2), (y - H / 2) / (H / 2)).astype(np.float32)
    return fr * (1 - k * np.clip(r - 0.35, 0, 1)[..., None] ** 1.5)
def shot_A(t):
    z = lerp(1.15, 1.21, eio(seg(t, 0, 5.2)))
    fr = foot('mpbox', 0.3 + t, z, 0.485, 0.53)
    p = eo(seg(t, 0, 1.0))
    if p < 1: fr = cv2.GaussianBlur(fr, (0, 0), 0.1 + (1 - p) * 10) * p
    return fr
def shot_E(t):
    z = lerp(1.04, 1.13, eio(seg(t, 21.7, 25.5)))
    fr = foot('ps5cine', 12.3 + (t - 21.9), z, 0.5, 0.5)
    return vignette_extra(fr * lerp(1, 0.86, eio(seg(t, 23.0, 25.0))), lerp(0.25, 0.75, eio(seg(t, 21.9, 25.0))))
def shot_G(t):
    return foot('boxes', 2.0 + (t - 33.66), lerp(1.06, 1.13, seg(t, 33.4, 35.8)), 0.5, 0.5)
_ink = {}
def shot_I(t):
    fr = foot('shelf', 62.0 + (t - 42.68), lerp(1.05, 1.13, seg(t, 42.5, 46.6)), 0.5, 0.5)
    if 'r' not in _ink:
        y, x = np.mgrid[0:H, 0:W].astype(np.float32); _ink['r'] = np.hypot((x - W / 2) / (W / 2), (y - H / 2) / (H / 2)) / 1.414
    sm = smoke(t)
    n = cv2.resize(L3[200:740, 300:1260], (W, H)) - 0.5
    r0 = lerp(1.15, 0.62, eio(seg(t, 42.7, 46.5)))
    m = np.clip((_ink['r'] + 0.35 * n - r0) / 0.22, 0, 1)[..., None]
    return fr * (1 - m) + sm * m
def shot_J(t):
    return foot('mpdisc', 14.0 + (t - 46.46), lerp(1.16, 1.22, seg(t, 46.3, 50.0)), 0.48, 0.54)
# ---------------- K: title ----------------
rngd = np.random.default_rng(5); ND = 150
DP = np.c_[rngd.uniform(0, W, ND), rngd.uniform(0, H, ND)]; DD = rngd.uniform(0.3, 1.0, ND); DV = rngd.uniform(-0.4, 0.4, ND)
L1T, L2T = 'WHO GETS TO KEEP', 'VIDEO GAMES'
def glyphs(s, fp, size, track, cy, t0, step):
    f = font(fp, size); adv = [f.getlength(c) for c in s]; tw = sum(adv) + track * size * (len(s) - 1)
    x = W / 2 - tw / 2; out = []; i = 0
    for c, a in zip(s, adv):
        if c != ' ': out.append((text_img(c, fp, size, 0), x + a / 2, cy, t0 + step * i)); i += 1
        x += a + track * size
    return out
GL = glyphs(L1T, LIGHT, 92, 0.34, 468, 50.05, 0.045) + glyphs(L2T, BOLD, 150, 0.10, 588, 50.55, 0.06)
def shot_K(t):
    ct = 24.1 + (t - 49.84) * 0.4
    fr = foot('mpdisc', ct, lerp(1.16, 1.3, eio(seg(t, 49.6, 61.9))), 0.5, 0.54, blend=True)
    fr = cv2.GaussianBlur(fr, (0, 0), lerp(2.5, 7, eo(seg(t, 49.84, 51.2)))) * lerp(0.62, 0.3, eo(seg(t, 49.84, 51.2)))
    fr = vignette_extra(fr, 0.6)
    # dust
    lay = np.zeros((H, W), np.float32)
    for (x, y), d, v in zip(DP, DD, DV):
        px = (x + (t - 49.84) * (10 + 22 * d)) % W; py = (y - (t - 49.84) * (6 + 14 * d) + 40 * v * math.sin(t * 0.4 + x)) % H
        cv2.circle(lay, (int(px), int(py)), max(1, int(1 + 2.6 * d)), 0.25 + 0.45 * d, -1, cv2.LINE_AA)
    fr += cv2.GaussianBlur(lay, (0, 0), 1.6)[..., None] * np.array([1.0, 0.92, 0.8], np.float32) * 0.6 * cl(seg(t, 49.84, 50.6))
    out = eio(seg(t, 59.9, 60.8))
    sx = (t - 51.95) / 0.95  # light streak position 0..1
    for a, gx_, gy_, t0 in GL:
        p = eo(seg(t, t0, t0 + 0.75))
        if p <= 0: continue
        boost = 1.0
        if 0 < sx < 1.3: boost += 1.4 * math.exp(-((gx_ - lerp(-300, W + 300, sx)) / 260) ** 2)
        put(fr, a, gx_, gy_ + (1 - p) * 18, (min(1, boost), min(1, boost), min(1, boost * 0.97)), p * (1 - out),
            (1 - p) * 14 + out * 16, 1 + (1 - p) * 0.12 + out * 0.04, 0.38 * boost)
    if -0.2 < sx < 1.3:
        xs = np.arange(W, dtype=np.float32); cxs = lerp(-300, W + 300, sx)
        prof = np.exp(-((xs - cxs) / 420) ** 2) * bump(sx, -0.2, 1.3)
        ys = np.arange(420, 640, dtype=np.float32)[:, None]
        core = np.exp(-((ys - 530) / 2.2) ** 2) * 1.2 + np.exp(-((ys - 530) / 26) ** 2) * 0.35
        fr[420:640] += (core * prof)[..., None] * np.array([1.0, 0.95, 0.88], np.float32)
    return fr * (1 - eio(seg(t, 60.4, 61.8)))
# ---------------- timeline ----------------
SHOTS = [(0, shot_A), (4.816, shot_B), (12.43, shot_D), (21.9, shot_E), (25.32, shot_F), (33.66, shot_G),
         (35.51, shot_H), (42.68, shot_I), (46.46, shot_J), (49.84, shot_K)]
DISSOLVE = {4.816, 21.9, 25.32, 33.66, 35.51, 42.68, 46.46, 49.84}
HW = 0.18
def compose(t):
    for i, (s, f) in enumerate(SHOTS):
        nxt = SHOTS[i + 1][0] if i + 1 < len(SHOTS) else 1e9
        if s <= t < nxt: cur, ci = f, i; break
    for i in range(1, len(SHOTS)):
        b = SHOTS[i][0]
        if b in DISSOLVE and b - HW <= t < b + HW:
            x = (t - (b - HW)) / (2 * HW); sg = 11 * math.sin(math.pi * x)
            A = cv2.GaussianBlur(SHOTS[i - 1][1](t), (0, 0), sg + 0.1); B = cv2.GaussianBlur(SHOTS[i][1](t), (0, 0), sg + 0.1)
            e = eio(x); return A * (1 - e) + B * e
    return cur(t)
yv, xv = np.mgrid[0:H, 0:W].astype(np.float32)
RV = np.hypot((xv - W / 2) / (W / 2), (yv - H / 2) / (H / 2)) / 1.414
VIGM = (1 - 0.5 * RV ** 2.4)[..., None].astype(np.float32)
del yv, xv
MR = cv2.getRotationMatrix2D((W / 2, H / 2), 0, 1.0022); MB = cv2.getRotationMatrix2D((W / 2, H / 2), 0, 0.9978)
def post(fr, n):
    fr = np.clip(fr, 0, 4)
    sm = cv2.resize(fr, (480, 270), interpolation=cv2.INTER_AREA)
    hi = np.maximum(sm - 0.6, 0); bl = cv2.GaussianBlur(hi, (0, 0), 5) * 0.7 + cv2.GaussianBlur(hi, (0, 0), 16) * 0.5
    fr = fr + cv2.resize(bl, (W, H), interpolation=cv2.INTER_LINEAR)
    fr = np.ascontiguousarray(fr)
    r = cv2.warpAffine(np.ascontiguousarray(fr[..., 0]), MR, (W, H), borderMode=cv2.BORDER_REPLICATE)
    b = cv2.warpAffine(np.ascontiguousarray(fr[..., 2]), MB, (W, H), borderMode=cv2.BORDER_REPLICATE)
    fr = np.dstack([r, fr[..., 1], b]) * VIGM
    fr = fr / (1 + np.maximum(fr - 0.85, 0) * 1.6)  # soft highlight roll-off
    g = np.random.default_rng(1000 + n).standard_normal((540, 960), dtype=np.float32) * (0.012 if 405 <= n < 660 else 0.03)
    fr = fr + cv2.resize(g, (W, H), interpolation=cv2.INTER_LINEAR)[..., None]
    return (np.clip(fr, 0, 1) * 255 + 0.5).astype(np.uint8)
def frame(n): return post(compose(n / FPS), n)

if __name__ == '__main__':
    if sys.argv[1] == 'test':
        for a in sys.argv[2:]:
            t = float(a); cv2.imwrite(f'{D}/' + os.environ.get('TD', 'test') + f'/{a}.jpg', cv2.resize(frame(int(round(t * FPS)))[:, :, ::-1], (640, 360), interpolation=cv2.INTER_AREA))
    else:
        a, b, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
        p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                              '-threads', '2', '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
        for n in range(a, b): p.stdin.write(frame(n).tobytes())
        p.stdin.close(); p.wait()

import re, json, asyncio, subprocess, edge_tts, os
L=open('guion.md').read().split('## 0:00')[1].split('\n',1)[1].split('### Fuentes')[0].splitlines()
items=[]
for l in L:
    l=l.strip()
    if not l or l.startswith('#') or l=='---' or l.startswith('0:00'): continue
    p=re.findall(r'⏸ ([\d,]+)s',l)
    cue=re.findall(r'`\[(.+?)\]`',l)
    if cue: items.append({'cue':cue[0]})
    if p: items.append({'pause':float(p[0].replace(',','.'))}); continue
    if cue: continue
    items.append({'text':l})
sem=asyncio.Semaphore(8)
def dur(f): return float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f]))
# edge-tts sometimes returns only the first syllable (0.36 s) without raising; the narration never runs faster than ~0.045 s per character
def ok(f,t): return os.path.exists(f) and os.path.getsize(f)>0 and dur(f)>=0.035*len(t)
async def say(i,t):
    f=f'tts/{i:03d}.mp3'
    if ok(f,t): return
    async with sem:
        for _ in range(6):
            try:
                await edge_tts.Communicate(t,'en-US-AndrewNeural',rate='+4%',proxy=os.environ['HTTPS_PROXY']).save(f)
                if ok(f,t): return
                err=RuntimeError(f'truncated audio for line {i}: {t}')
            except Exception as e: err=e
        raise err
async def main(): await asyncio.gather(*[say(i,it['text']) for i,it in enumerate(items) if 'text' in it])
asyncio.run(main())
t=0; words=0
for i,it in enumerate(items):
    if 'text' in it:
        d=dur(f'tts/{i:03d}.mp3')
        it.update(i=i,start=t,dur=d); t+=d; words+=len(it['text'].split())
        nxt=[x for x in items[i+1:i+3]]
        if not any('pause' in x for x in nxt[:1]) and not (nxt and 'cue' in nxt[0] and len(nxt)>1 and 'pause' in nxt[1]):
            t+=0.4 if it['text'][-1] in '.?!"…' else 0.15
    elif 'pause' in it: it['start']=t; t+=it['pause']
    elif 'cue' in it: it['start']=t
json.dump({'items':items,'total':t},open('timeline.json','w'),indent=0)
speech=sum(x.get('dur',0) for x in items)
print(f'total {t/60:.2f} min, words {words}, wpm speech-only {words/speech*60:.0f}, overall {words/t*60:.0f}')

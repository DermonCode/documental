import json, subprocess, urllib.request, os, sys
from concurrent.futures import ThreadPoolExecutor
APPS={'clair':1903340,'silksong':1030300,'schedule':3164500,'repo':3241660,'spidey':2651280,'tlou':2531310,'gow':2322010,'horizon':2420110,'acmap':3159330,'skyrim':489830,'fallout4':377160,'outerwilds':753640}
def get(k):
    out=f'clips/{k}.mp4'
    if os.path.exists(out): return k,'cached'
    d=json.load(urllib.request.urlopen(f'https://store.steampowered.com/api/appdetails?appids={APPS[k]}&filters=movies'))
    m=list(d.values())[0]['data']['movies'][0]
    tmp=f'clips/{k}.full.mp4'
    r=subprocess.run(['yt-dlp','-q','--no-warnings','-f','bv*[height<=1080]/bv*/b','-o',tmp,m['hls_h264']],capture_output=True,text=True)
    if not os.path.exists(tmp): return k,'FAIL '+r.stderr[-200:]
    subprocess.run(['ffmpeg','-v','error','-y','-i',tmp,'-an','-vf','scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,fps=30','-c:v','libx264','-preset','veryfast','-crf','20',out])
    os.remove(tmp); return k,m['name']
with ThreadPoolExecutor(4) as ex:
    for k,m in ex.map(get, APPS): print(k,m,flush=True)

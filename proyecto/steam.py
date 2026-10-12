import json, subprocess, urllib.request, os
from concurrent.futures import ThreadPoolExecutor
# official Steam trailers, downloaded at 1080p into src/ (cut later by dl.py)
# value: app id, or (app id, index in the store's trailer list)
APPS={'clair':1903340,'silksong':1030300,'schedule':3164500,'repo':3241660,'spidey':2651280,'tlou':2531310,'gow':2322010,'horizon':2420110,'acs':3159330,'spideypc':(2651280,1),'spideyrev':(2651280,2)}
os.makedirs('src',exist_ok=True)
def get(k):
    out=f'src/steam_{k}.mp4'
    if os.path.exists(out): return k,'cached'
    app,n=APPS[k] if isinstance(APPS[k],tuple) else (APPS[k],0)
    d=json.load(urllib.request.urlopen(f'https://store.steampowered.com/api/appdetails?appids={app}&filters=movies'))
    m=list(d.values())[0]['data']['movies'][n]
    r=subprocess.run(['yt-dlp','-q','--no-warnings','-f','bv*[height=1080]/bv*[height>=1080]','-o',out,m['hls_h264']],capture_output=True,text=True)
    return k,(m['name'] if os.path.exists(out) else 'FAIL '+r.stderr[-200:])
with ThreadPoolExecutor(4) as ex:
    for k,m in ex.map(get, APPS): print(k,m,flush=True)

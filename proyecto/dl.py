import subprocess, json, os, sys
from concurrent.futures import ThreadPoolExecutor
from plan import CLIPS
C='/tmp/claude-0/-home-user/7cf0b011-4150-5a77-bccc-5f099c31e6a8/scratchpad/cookies.txt'
B=['yt-dlp','-q','--no-warnings','--js-runtimes','node','--cookies',C]
def get(k):
    out=f'clips/{k}.mp4'
    if os.path.exists(out): return k,'cached'
    try:
        res=subprocess.run(B+['--flat-playlist','--print','%(id)s\t%(duration)s\t%(title)s',f'ytsearch8:{CLIPS[k]}'],capture_output=True,text=True,timeout=180).stdout.splitlines()
        vid,d,title=next(r.split('\t') for r in res if r.split('\t')[1] not in ('NA','None') and 40<float(r.split('\t')[1])<1500)
        d=float(d); info={'title':title,'webpage_url':'https://www.youtube.com/watch?v='+vid}; s=min(45,d*0.15); e=min(d-5,s+90)
        full=f'clips/{k}.full'
        r=subprocess.run(B+['-f','bv*[height<=720][vcodec^=avc1]/bv*[height<=720]','-N','4','--sleep-requests','1','-o',full+'.%(ext)s',info['webpage_url']],capture_output=True,text=True,timeout=900)
        src=[f for f in os.listdir('clips') if f.startswith(k+'.full.')]
        if src:
            subprocess.run(['ffmpeg','-v','error','-y','-ss',str(s),'-to',str(e),'-i','clips/'+src[0],'-an','-vf','scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,fps=30','-c:v','libx264','-preset','veryfast','-crf','20',out])
            os.remove('clips/'+src[0])
        return k, f"{info['title'][:60]} | {info['webpage_url']} | {'OK' if os.path.exists(out) else r.stderr[-200:]}"
    except Exception as ex: return k, f'FAIL {ex}'
with ThreadPoolExecutor(2) as ex:
    for k,m in ex.map(get, sys.argv[1:] or CLIPS): print(k,m,flush=True)

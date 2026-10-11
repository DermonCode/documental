import subprocess, os, sys
from concurrent.futures import ThreadPoolExecutor
from clips import CLIPS
# cut each range from the best source at or above 1080p and normalise to 1920x1080 / 30 fps
C=os.environ.get('YT_COOKIES','cookies.txt')
B=['yt-dlp','-q','--no-warnings','--js-runtimes','node','--cookies',C]
NORM='scale=1920:1080:force_original_aspect_ratio=decrease:flags=lanczos,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30'
os.makedirs('clips',exist_ok=True)
def get(k):
    src,a,b=CLIPS[k]; out=f'clips/{k}.mp4'
    if os.path.exists(out): return k,'cached'
    if src.startswith('steam_'): inp=['-ss',str(a),'-to',str(b),'-i',f'src/{src}.mp4']; tmp=None
    else:
        tmp=f'clips/{k}.part.mkv'
        r=subprocess.run(B+['-f','bv*[height>=1072][height<=2160]','-S','res,fps','--download-sections',f'*{a}-{b}','--merge-output-format','mkv','-o',tmp,'--',src],capture_output=True,text=True)
        if not os.path.exists(tmp): return k,'FAIL '+r.stderr[-300:]
        inp=['-i',tmp]
    subprocess.run(['ffmpeg','-v','error','-y']+inp+['-an','-vf',NORM,'-c:v','libx264','-preset','medium','-crf','17','-pix_fmt','yuv420p',out],check=True)
    h=subprocess.check_output(['ffprobe','-v','error','-select_streams','v','-show_entries','stream=height','-of','csv=p=0']+([tmp] if tmp else [f'src/{src}.mp4'])).decode().strip()
    if tmp: os.remove(tmp)
    return k,f'source {h}p'
with ThreadPoolExecutor(3) as ex:
    for k,m in ex.map(get, sys.argv[1:] or CLIPS): print(k,m,flush=True)

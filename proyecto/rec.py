import os, glob
from playwright.sync_api import sync_playwright
exe=glob.glob('/opt/pw-browsers/chromium-*/chrome-linux*/chrome')[0]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=exe,proxy={'server':os.environ['HTTPS_PROXY']})
    c=b.new_context(viewport={'width':1920,'height':1080},record_video_dir='gfx/rec',record_video_size={'width':1920,'height':1080})
    pg=c.new_page(); pg.goto('https://store.steampowered.com/search/?sort_by=Released_DESC&category1=998',wait_until='load',timeout=60000)
    pg.wait_for_timeout(2000)
    for _ in range(300): pg.mouse.wheel(0,9); pg.wait_for_timeout(100)
    c.close(); b.close()
import subprocess
os.makedirs('clips',exist_ok=True)
subprocess.run(['ffmpeg','-v','error','-y','-ss','2','-i',glob.glob('gfx/rec/*.webm')[0],'-vf','fps=30','-c:v','libx264','-crf','17','-pix_fmt','yuv420p','clips/steam.mp4'],check=True)

# Descarga y normaliza (1080p30, crf 16) los clips de la sección 1 en ./clips
import os, subprocess, sys
D = os.path.dirname(os.path.abspath(__file__))
CLIPS = {'mpbox': ('pEqgewp9DTc', 0, 40), 'mpdisc': ('pEqgewp9DTc', 289, 330), 'shelf': ('4iSpL_-hO8Y', 200, 280),
         'boxes': ('4iSpL_-hO8Y', 450, 510), 'ps5cine': ('xm3VHjZl4DU', 172, 221)}
os.makedirs(f'{D}/clips', exist_ok=True)
for k, (vid, a, b) in CLIPS.items():
    raw = f'{D}/clips/{k}_raw.mp4'
    subprocess.run([sys.executable, '-m', 'yt_dlp', '-q', '-f', 'bv*[height<=1080]+ba/b', '--download-sections', f'*{a}-{b}',
                    '--force-keyframes-at-cuts', '--merge-output-format', 'mp4', '-o', raw, f'https://www.youtube.com/watch?v={vid}'], check=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', raw, '-an', '-vf', 'scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=30',
                    '-threads', '2', '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p', f'{D}/clips/{k}.mp4'], check=True)
    os.remove(raw); print(k, 'ok')

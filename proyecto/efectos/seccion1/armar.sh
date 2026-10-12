#!/bin/sh
# Uso: sh armar.sh documental_v3_completo.mp4 salida.mp4
# Render en 4 procesos (no satura la PC); cada uno con ffmpeg -threads 2.
set -e; cd "$(dirname "$0")"
V="$1"; OUT="$2"
[ -d clips ] || python clips.py
ffmpeg -v error -y -i "$V" -t 61.844 -vn a.wav
mkdir -p parts; N=1855; S=$(( (N + 3) / 4 )); : > parts.txt
for i in 0 1 2 3; do a=$((i * S)); b=$(( a + S < N ? a + S : N )); python render.py $a $b parts/p$i.mp4 & echo "file 'parts/p$i.mp4'" >> parts.txt; done
wait
ffmpeg -v error -y -f concat -safe 0 -i parts.txt -i a.wav -map 0:v -map 1:a -c:v copy -af "afade=t=out:st=60.6:d=1.24" -c:a aac -b:a 192k "$OUT"

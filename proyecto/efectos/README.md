# Efectos

Re-edición del documental por secciones, con efectos y animaciones compuestos por frame en Python (numpy + OpenCV + Pillow) y codificados con ffmpeg.

- `seccion1/render.py`: cold open (0:00–1:01.8). `python render.py test 15.5 37.2` genera stills en `test/`; `python render.py A B out.mp4` renderiza los frames A..B.
- `seccion1/clips.py`: descarga y normaliza los clips de stock (yt-dlp + ffmpeg).
- `seccion1/armar.sh`: arma la sección completa con el audio del video base.
- `tile.py`: hoja de contacto para revisar stills (`python tile.py carpeta salida.jpg columnas`).

Requisitos: Python 3 con numpy, opencv-python, Pillow y yt-dlp; ffmpeg en el PATH; fuentes Segoe UI (Windows).

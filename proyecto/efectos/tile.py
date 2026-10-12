import sys, glob, os
from PIL import Image
fs = sorted(glob.glob(sys.argv[1] + '/*.jpg'), key=lambda p: float(os.path.basename(p)[:-4])); c = int(sys.argv[3])
w, h = Image.open(fs[0]).size; o = Image.new('RGB', (w * c + 2 * c, (h + 2) * ((len(fs) + c - 1) // c)))
for i, f in enumerate(fs): o.paste(Image.open(f), ((i % c) * (w + 2), (i // c) * (h + 2)))
o.save(sys.argv[2], quality=82); print(len(fs))

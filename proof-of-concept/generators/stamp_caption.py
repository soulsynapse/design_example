# Stamps the proof-of-concept caption band onto an image produced by an external generator,
# so that nothing in this folder can be mistaken for project work. Same band as make_render.py.
# Usage: python stamp_caption.py <in.png|jpg> <out.png> "<caption line, e.g. R-01  ·  ...  ·  vendimia, 18:45>"
import sys
from PIL import Image, ImageDraw, ImageFont

src, dst, t1 = sys.argv[1], sys.argv[2], sys.argv[3]
im = Image.open(src).convert("RGB")
W, H = im.size
k = W / 3840.0                                   # scale the band with the image
draw = ImageDraw.Draw(im)
try:
    f1 = ImageFont.truetype("arial.ttf", max(12, int(34 * k))); f2 = ImageFont.truetype("arial.ttf", max(10, int(26 * k)))
except Exception:
    f1 = f2 = ImageFont.load_default()
t2 = "PRUEBA DE CONCEPTO — imagen generada con herramienta externa a partir del ejemplo; no es el proyecto."
w1 = draw.textlength(t1, font=f1); w2 = draw.textlength(t2, font=f2)
pad = int(28 * k)
bx0 = W - max(w1, w2) - 2 * pad - int(40 * k); by0 = H - int(130 * k)
draw.rectangle((bx0, by0, W - int(40 * k), H - int(40 * k)), fill=(20, 18, 16))
draw.text((bx0 + pad, by0 + int(16 * k)), t1, font=f1, fill=(236, 230, 220))
draw.text((bx0 + pad, by0 + int(60 * k)), t2, font=f2, fill=(226, 120, 100))
im.save(dst)
print("stamped", dst, W, "x", H)

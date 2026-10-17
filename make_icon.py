from PIL import Image, ImageDraw

S = 1024
top, bottom = (79, 156, 255), (27, 79, 216)
g = Image.linear_gradient("L").resize((S, S))
base = Image.composite(Image.new("RGB", (S, S), bottom), Image.new("RGB", (S, S), top), g).convert("RGBA")

mask = Image.new("L", (S, S), 0)
ImageDraw.Draw(mask).rounded_rectangle((0, 0, S - 1, S - 1), radius=int(S * 0.22), fill=255)
base.putalpha(mask)

ov = Image.new("RGBA", (S, S), (0, 0, 0, 0))
d = ImageDraw.Draw(ov)
p = lambda v: int(v * S)
sw, hw, r = 0.05, 0.13, p(0.03)

# seta de download (branca)
cx = 0.34
d.rounded_rectangle((p(cx - sw), p(0.18), p(cx + sw), p(0.55)), radius=r, fill=(255, 255, 255, 255))
d.polygon([(p(cx - hw), p(0.50)), (p(cx + hw), p(0.50)), (p(cx), p(0.75))], fill=(255, 255, 255, 255))

# seta de upload (azul-claro)
cx = 0.66
c = (170, 232, 255, 255)
d.rounded_rectangle((p(cx - sw), p(0.45), p(cx + sw), p(0.82)), radius=r, fill=c)
d.polygon([(p(cx - hw), p(0.50)), (p(cx + hw), p(0.50)), (p(cx), p(0.25))], fill=c)

img = Image.alpha_composite(base, ov).resize((256, 256), Image.LANCZOS)
img.save("AlfTorrent.ico", format="ICO", sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])

"""Vice City Moments branding: profile picture (800x800) and banner (2560x1440)."""
import glob
import os
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FONT = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
FONT_I = "/usr/share/fonts/opentype/inter/InterDisplay-BlackItalic.otf"
PINK = (255, 46, 160)
ORANGE = (255, 150, 40)
YELLOW = (255, 214, 10)
CYAN = (40, 230, 255)
NAVY = (12, 6, 34)
PURPLE = (70, 16, 110)


def vgrad(w, h, top, bottom):
    t = np.linspace(0, 1, h)[:, None, None]
    a = np.array(top)[None, None, :] * (1 - t) + np.array(bottom)[None, None, :] * t
    return Image.fromarray(np.repeat(a, w, axis=1).astype(np.uint8))


def sun(size, stripes=True):
    """Striped retro sun, RGBA."""
    s = vgrad(size, size, YELLOW, PINK).convert("RGBA")
    mask = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(mask)
    d.ellipse([0, 0, size - 1, size - 1], fill=255)
    if stripes:
        y = int(size * 0.55)
        gap, k = int(size * 0.025), 0
        while y < size:
            th = int(size * 0.012) + k * int(size * 0.008)
            d.rectangle([0, y, size, y + th], fill=0)
            y += th + gap
            k += 1
    s.putalpha(mask)
    return s


def grid(w, h, color=PINK, horizon=0.0):
    """Perspective synthwave floor grid, RGBA."""
    g = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(g)
    cx = w / 2
    for i in range(-14, 15):
        x_far = cx + i * w * 0.035
        x_near = cx + i * w * 0.32
        d.line([(x_far, 0), (x_near, h)], fill=color + (200,), width=max(2, w // 300))
    y, step = 2.0, 6.0
    while y < h:
        d.line([(0, y), (w, y)], fill=color + (200,), width=max(2, w // 300))
        y += step
        step *= 1.35
    fade = vgrad(w, h, (0, 0, 0), (255, 255, 255)).convert("L")
    a = np.array(g.split()[3]).astype(float) * (np.array(fade).astype(float) / 255) ** 0.6
    g.putalpha(Image.fromarray(a.astype(np.uint8)))
    return g


def glow_text(img, xy, text, font, fill, glow, anchor="mm", radius=18, stroke=0):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).text(xy, text, font=font, fill=glow + (255,), anchor=anchor, stroke_width=stroke + 6,
                               stroke_fill=glow + (255,))
    layer = layer.filter(ImageFilter.GaussianBlur(radius))
    img.alpha_composite(layer)
    img.alpha_composite(layer)
    ImageDraw.Draw(img).text(xy, text, font=font, fill=fill, anchor=anchor, stroke_width=stroke,
                             stroke_fill=(20, 0, 40))


def profile(out):
    S = 800
    img = vgrad(S, S, NAVY, PURPLE).convert("RGBA")
    sz = int(S * 0.62)
    img.alpha_composite(sun(sz), ((S - sz) // 2, int(S * 0.10)))
    fl = grid(S, int(S * 0.36))
    floor_bg = Image.new("RGBA", fl.size, NAVY + (255,))
    floor_bg.alpha_composite(fl)
    img.alpha_composite(floor_bg, (0, S - fl.height))
    ImageDraw.Draw(img).line([(0, S - fl.height), (S, S - fl.height)], fill=CYAN, width=6)
    f = ImageFont.truetype(FONT_I, 300)
    glow_text(img, (S // 2 - 6, int(S * 0.55)), "VCM", f, (255, 255, 255), PINK, radius=22, stroke=4)
    img.convert("RGB").save(out, quality=95)


def banner(out, bg_path):
    W, H = 2560, 1440
    bg = Image.open(bg_path).convert("RGB")
    bw = W
    bh = int(bg.height * W / bg.width)
    bg = bg.resize((bw, bh), Image.LANCZOS)
    top = max((bh - H) // 2 - 80, 0)
    bg = bg.crop((0, top, W, top + H)).convert("RGBA")
    # darken + purple/pink grade
    shade = vgrad(W, H, (20, 6, 50), (60, 10, 70)).convert("RGBA")
    shade.putalpha(165)
    bg.alpha_composite(shade)
    # vignette band behind the safe area
    band = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(band).rectangle([0, 470, W, 970], fill=(10, 2, 26, 150))
    band = band.filter(ImageFilter.GaussianBlur(60))
    bg.alpha_composite(band)
    # safe area: 1546 x 423 centred -> x 507..2053, y 508..931
    logo = Image.open(out.replace("banner", "profile")).convert("RGBA").resize((330, 330), Image.LANCZOS)
    m = Image.new("L", logo.size, 0)
    ImageDraw.Draw(m).ellipse([0, 0, 329, 329], fill=255)
    logo.putalpha(m)
    ring = Image.new("RGBA", (350, 350), (0, 0, 0, 0))
    ImageDraw.Draw(ring).ellipse([0, 0, 349, 349], fill=PINK + (255,))
    ring = ring.filter(ImageFilter.GaussianBlur(6))
    bg.alpha_composite(ring, (530, 545))
    bg.alpha_composite(logo, (540, 555))
    def fit(path, text, maxw, start):
        size = start
        f = ImageFont.truetype(path, size)
        while f.getlength(text) > maxw:
            size -= 2
            f = ImageFont.truetype(path, size)
        return f
    x0, maxw = 920, 2030 - 920
    f1 = fit(FONT_I, "VICE CITY MOMENTS", maxw, 150)
    glow_text(bg, (x0, 650), "VICE CITY MOMENTS", f1, (255, 255, 255), PINK, anchor="lm", radius=18, stroke=3)
    f2 = fit(FONT, "NEW GTA 6 SHORTS EVERY DAY", maxw, 64)
    glow_text(bg, (x0 + 4, 778), "NEW GTA 6 SHORTS EVERY DAY", f2, YELLOW, ORANGE, anchor="lm", radius=14, stroke=2)
    f3 = fit(FONT, "Clips  •  News  •  Edits  •  Vice City", maxw, 44)
    ImageDraw.Draw(bg).text((x0 + 6, 858), "Clips  •  News  •  Edits  •  Vice City", font=f3, fill=(225, 210, 255),
                            anchor="lm")
    bg.convert("RGB").save(out, quality=92)


if __name__ == "__main__":
    outdir = sys.argv[1]
    os.makedirs(outdir, exist_ok=True)
    profile(os.path.join(outdir, "profile.jpg"))
    banner(os.path.join(outdir, "banner.jpg"), sys.argv[2])
    print("done")

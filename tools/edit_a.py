"""'Days we waited' counter edit – original VCM format, cut to the beat of
'Blood In Your Eyes' (Tove Lo, GTA VI album) as the TikTok sound.
Beat drop at 5.07 s, then ~113 BPM (0.531 s per beat)."""
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from render import build, W, H, FONT, YELLOW, PINK

DROP = 5.07
BEAT = 0.531
END = 12.0

# intro: year milestones (cut points from the song's intro hits)
intro = [  # (t0, t1, shot, xc, year, label, days_at_start, days_at_end)
    (0.00, 0.79, "Jason_and_Lucia_01", 0.47, "2013", "GTA 5 COMES OUT", 0, 600),
    (0.79, 1.86, "Leonida_Keys_01", 0.62, "2018", "STILL WAITING...", 1567, 2600),
    (1.86, 2.93, "Vice_City_10", 0.30, "2022", "GTA 6 CONFIRMED", 3062, 3500),
    (2.93, 4.00, "Lucia_Caminos_11", 0.64, "2023", "TRAILER 1 DROPS", 3731, 4200),
    (4.00, DROP, "Vice_City_27", 0.50, "2025", "DELAYED. TWICE.", 4433, 4800),
]
fast = [("Jason_and_Lucia_11", 0.45), ("Vice_City_11", 0.35), ("Jason_Duval_11", 0.50),
        ("Lucia_Caminos_13", 0.45), ("Vice_City_15", 0.55), ("Jason_and_Lucia_09", 0.50),
        ("Vice_City_24", 0.45), ("Lucia_Caminos_10", 0.55), ("Jason_Duval_17", 0.50),
        ("Vice_City_17", 0.50)]

segs = []
for t0, t1, shot, xc, *_ in intro:
    segs.append(dict(img=shot, xc=xc, z0=1.0, z1=1.12, dur=t1 - t0, punch=True))
t = DROP
for shot, xc in fast:
    segs.append(dict(img=shot, xc=xc, z0=1.06, z1=1.0, dur=BEAT, punch=True))
    t += BEAT
segs.append(dict(img="Jason_and_Lucia_16", xc=0.32, z0=1.0, z1=1.1, dur=END - t, punch=False))
END_CARD = t

F_NUM = ImageFont.truetype(FONT, 250)
F_YEAR = ImageFont.truetype(FONT, 120)
F_LAB = ImageFont.truetype(FONT, 66)
F_TOP = ImageFont.truetype(FONT, 58)


def days_at(t):
    if t >= DROP:
        return 4810
    for t0, t1, _, _, _, _, d0, d1 in intro:
        if t0 <= t < t1:
            return int(d0 + (d1 - d0) * (t - t0) / (t1 - t0))
    return 0


def ctext(d, y, txt, font, fill, stroke=10, glow=None, frame=None):
    w = font.getlength(txt)
    x = (W - w) / 2
    if glow is not None:
        g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(g).text((x, y), txt, font=font, fill=glow + (200,), stroke_width=stroke + 14, stroke_fill=glow + (120,))
        from PIL import ImageFilter
        frame.alpha_composite(g.filter(ImageFilter.GaussianBlur(18)))
    d.text((x + 5, y + 7), txt, font=font, fill=(0, 0, 0, 170), stroke_width=stroke, stroke_fill=(0, 0, 0, 170))
    d.text((x, y), txt, font=font, fill=fill, stroke_width=stroke, stroke_fill=(0, 0, 0))


def overlay(frame, t):
    if t >= END_CARD:
        return
    d = ImageDraw.Draw(frame)
    ctext(d, 400, "DAYS WE WAITED FOR GTA 6", F_TOP, (255, 255, 255), stroke=8)
    n = days_at(t)
    ctext(d, 470, f"{n:,}", F_NUM, (255, 255, 255), stroke=12, glow=PINK, frame=frame)
    # progress bar
    bx, by, bw, bh = 160, 790, 760, 26
    d.rounded_rectangle([bx - 4, by - 4, bx + bw + 4, by + bh + 4], 16, fill=(0, 0, 0, 200))
    fill = int(bw * min(n / 4811, 1))
    if fill > 4:
        grad = np.linspace(0, 1, fill)[None, :, None]
        a = np.array(PINK)[None, None, :] * (1 - grad) + np.array(YELLOW)[None, None, :] * grad
        bar = Image.fromarray(np.repeat(a, bh, 0).astype(np.uint8)).convert("RGBA")
        mask = Image.new("L", (fill, bh), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, fill - 1, bh - 1], 12, fill=255)
        frame.paste(bar, (bx, by), mask)
    if t < DROP:
        for t0, t1, _, _, year, label, *_ in intro:
            if t0 <= t < t1:
                age = (t - t0) * 30
                sc = 1 + 0.3 * max(0, 1 - age / 5) ** 2
                fy = ImageFont.truetype(FONT, int(120 * sc))
                ctext(d, 860 - (sc - 1) * 60, year, fy, YELLOW, stroke=10)
                ctext(d, 1000, label, F_LAB, (255, 255, 255), stroke=8)


def grade(img, t):
    img = ImageEnhance.Contrast(img).enhance(1.08)
    img = ImageEnhance.Color(img).enhance(1.12)
    a = np.asarray(img).astype(np.float32)
    yy, xx = np.ogrid[:H, :W]
    v = 1 - 0.35 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) / 2
    return Image.fromarray(np.clip(a * v[..., None], 0, 255).astype(np.uint8))


texts = [
    dict(t0=DROP, t1=END_CARD, lines=[("1 DAY LEFT", YELLOW)], size=170, y=930),
    dict(t0=END_CARD, t1=END + 1, lines=[("SEE YOU IN", None), ("VICE CITY", YELLOW)], size=150, y=620),
    dict(t0=END_CARD + 0.5, t1=END + 1, lines=[("READY? YES OR NO", None)], size=80, y=880, pop=True),
]
flashes = [DROP]

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "out/05_days_waited.mp4"
    if len(sys.argv) > 2:  # preview mode: list of times
        import render
        times = [float(x) for x in sys.argv[2:]]
        render.build.__globals__  # noqa
    build(segs, texts, out, flashes=flashes, overlay=overlay, grade=grade)

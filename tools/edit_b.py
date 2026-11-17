"""'Welcome to Leonida' launch-day edit – original VCM format, cut to the beat of
'RUPTURE (Super Slowed)' (chief doro & CASAP) as the TikTok sound.
Beats every ~0.868 s from 0.15 s, big drop at 7.10 s."""
import sys
from PIL import Image, ImageDraw, ImageFont
from render import build, W, H, FONT, YELLOW, PINK
from edit_a import ctext, grade

DROP = 7.10
B = 0.87
BAR = 300  # letterbox height during the intro

intro = [  # (t0, t1, shot, xc, z0, z1)
    (0.00, 1.89, "Vice_City_27", 0.50, 1.00, 1.10),
    (1.89, 3.63, "Leonida_Keys_01", 0.60, 1.00, 1.10),
    (3.63, 5.37, "Jason_and_Lucia_13", 0.50, 1.00, 1.12),
    (5.37, DROP, "Vice_City_01", 0.45, 1.00, 1.15),
]
regions = [("Vice_City_10", 0.30, "VICE CITY"), ("Leonida_Keys_03", 0.45, "LEONIDA KEYS"),
           ("Grassrivers_04", 0.55, "GRASSRIVERS"), ("Port_Gellhorn_06", 0.50, "PORT GELLHORN"),
           ("Ambrosia_01", 0.50, "AMBROSIA"), ("Mount_Kalaga_National_Park_02", 0.55, "MOUNT KALAGA")]
action = [("Jason_Duval_11", 0.50), ("Jason_and_Lucia_17", 0.45), ("Jason_Duval_05", 0.45), ("Jason_and_Lucia_19", 0.50)]

segs = [dict(img=s, xc=x, z0=a, z1=b, dur=t1 - t0, punch=False) for t0, t1, s, x, a, b in intro]
t = DROP
reg_times = []
for s, x, name in regions:
    segs.append(dict(img=s, xc=x, z0=1.08, z1=1.0, dur=B, punch=True))
    reg_times.append((t, t + B, name))
    t += B
for s, x in action:
    segs.append(dict(img=s, xc=x, z0=1.1, z1=1.0, dur=B / 2, punch=True))
    t += B / 2
END_CARD = t
END = END_CARD + 1.6
segs.append(dict(img="Vice_City_03", xc=0.5, z0=1.0, z1=1.08, dur=END - END_CARD, punch=False))

F_REG = ImageFont.truetype(FONT, 140)
F_IDX = ImageFont.truetype(FONT, 60)


def overlay(frame, t):
    d = ImageDraw.Draw(frame)
    if t < DROP:
        d.rectangle([0, 0, W, BAR], fill=(0, 0, 0, 255))
        d.rectangle([0, H - BAR, W, H], fill=(0, 0, 0, 255))
    for k, (t0, t1, name) in enumerate(reg_times):
        if t0 <= t < t1:
            age = (t - t0) * 30
            sc = 1 + 0.3 * max(0, 1 - age / 5) ** 2
            ctext(d, 760, f"0{k + 1} / 06", F_IDX, PINK, stroke=8)
            f = ImageFont.truetype(FONT, int(140 * sc))
            while f.getlength(name) > 980:
                f = ImageFont.truetype(FONT, f.size - 6)
            ctext(d, 850 - (sc - 1) * 70, name, f, YELLOW, stroke=12)


texts = [
    dict(t0=0.0, t1=1.89, lines=[("AFTER 4,811 DAYS...", None)], size=86, y=820, pop=False),
    dict(t0=1.89, t1=3.63, lines=[("IT'S FINALLY", None), ("HERE", YELLOW)], size=120, y=820),
    dict(t0=3.63, t1=5.37, lines=[("GTA 6 IS OUT", YELLOW)], size=130, y=820),
    dict(t0=5.37, t1=DROP, lines=[("WELCOME TO", None), ("LEONIDA", YELLOW)], size=140, y=820),
    dict(t0=END_CARD, t1=END + 1, lines=[("WHERE ARE YOU", None), ("GOING FIRST?", YELLOW)], size=130, y=700),
]

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "out/06_welcome_to_leonida.mp4"
    print("END", END)
    build(segs, texts, out, flashes=[DROP], overlay=overlay, grade=grade)

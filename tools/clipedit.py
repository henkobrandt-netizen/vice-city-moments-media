"""Beat-synced vertical edits from official 16:9 trailer footage.

shot dict: src (path), start (s in source), dur (s in output), xc (crop centre 0-1, default .5),
           yc (0-1, default .5), z (extra zoom >=1, default 1), speed (source speed, default 1),
           punch (bool, zoom-in kick on the cut), shake (bool)
text dict: t0, t1, lines [(text, color|None)], size, y (centre px), pop (bool)
fx: flashes [t...], letterbox (t0, t1, bar_px)
"""
import subprocess, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1080, 1920, 30
FONT = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
YELLOW = (255, 214, 10)
PINK = (255, 92, 190)
WORK_H = 2112  # decode height (10% headroom for punch-ins)
WORK_W = WORK_H * 9 // 16
# real picture area inside each source (trailers are letterboxed): (top, height)
ACTIVE = {"launch": (60, 960), "t2": (108, 864), "t1": (0, 1080), "preload": (60, 960), "festival": (0, 1080)}


def text_block(lines, size=110, color=(255, 255, 255), stroke=10, max_w=960):
    rendered = []
    for txt, col in lines:
        s = size
        font = ImageFont.truetype(FONT, s)
        while font.getlength(txt) > max_w and s > 40:
            s -= 4
            font = ImageFont.truetype(FONT, s)
        rendered.append((txt, col or color, font, s))
    pad = stroke * 2 + 12
    heights = [int(s * 1.1) for *_, s in rendered]
    bw, bh = max_w + pad * 2, sum(heights) + pad * 2
    img = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    sh = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    d, ds = ImageDraw.Draw(img), ImageDraw.Draw(sh)
    y = pad
    for (txt, col, font, s), lh in zip(rendered, heights):
        x = (bw - font.getlength(txt)) / 2
        ds.text((x + 5, y + 7), txt, font=font, fill=(0, 0, 0, 170), stroke_width=stroke, stroke_fill=(0, 0, 0, 170))
        d.text((x, y), txt, font=font, fill=col, stroke_width=stroke, stroke_fill=(0, 0, 0))
        y += lh
    return Image.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)), img)


def decode_shot(s, nframes, ww=None, wh=None, aspect=9 / 16):
    """Yield nframes RGB arrays (ww x wh) for one shot."""
    ww, wh = ww or WORK_W, wh or WORK_H
    speed = s.get("speed", 1.0)
    z = s.get("z", 1.0)
    import os
    top, ah = ACTIVE.get(os.path.basename(s["src"]).split(".")[0], (0, 1080))
    ch = ah / z
    cw = min(ch * aspect, 1920)
    ch = cw / aspect
    x0 = min(max(s.get("xc", 0.5) * 1920 - cw / 2, 0), 1920 - cw)
    y0 = top + min(max(s.get("yc", 0.5) * ah - ch / 2, 0), ah - ch)
    src_dur = nframes / FPS * speed + 0.2
    vf = (f"crop={cw:.1f}:{ch:.1f}:{x0:.1f}:{y0:.1f},"
          f"scale={ww}:{wh}:flags=lanczos,"
          f"setpts=PTS/{speed},fps={FPS},"
          "eq=contrast=1.07:saturation=1.18:gamma=0.98,unsharp=5:5:0.6")
    cmd = ["ffmpeg", "-v", "error", "-ss", f"{s['start']:.3f}", "-t", f"{src_dur:.3f}", "-i", s["src"],
           "-vf", vf, "-frames:v", str(nframes), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    fsz = ww * wh * 3
    last = None
    for _ in range(nframes):
        buf = p.stdout.read(fsz)
        if len(buf) == fsz:
            last = np.frombuffer(buf, np.uint8).reshape(wh, ww, 3)
        yield last
    p.stdout.close()
    p.wait()


_vig = None


def vignette(a):
    global _vig
    h, w = a.shape[:2]
    if _vig is None or _vig.shape[:2] != (h, w):
        yy, xx = np.ogrid[:h, :w]
        _vig = (1 - 0.32 * (((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2) / 2)[..., None]
    return (a * _vig).astype(np.uint8)


def build(shots, texts, out, flashes=(), letterbox=None, shake_at=(), rotated=False, text_max_w=960):
    """rotated=True: compose on a 1920x1080 landscape canvas (full cinematic frame, no crop)
    and rotate it 90 degrees into a 1080x1920 file (viewers turn the phone)."""
    CW, CH = (1920, 1080) if rotated else (W, H)
    ww, wh = (int(CW * 1.1) // 2 * 2, int(CH * 1.1) // 2 * 2)
    aspect = CW / CH
    total = sum(s["dur"] for s in shots)
    n_total = int(round(total * FPS))
    tblocks = []
    for t in texts:
        img = text_block(t["lines"], t.get("size", 110), max_w=t.get("max_w", text_max_w))
        tblocks.append((t, img))
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
                            "-shortest", "-c:v", "libx264", "-preset", "medium", "-crf", "15", "-profile:v", "high",
                            "-tune", "film", "-pix_fmt", "yuv420p", "-c:a", "aac", "-movflags", "+faststart", out],
                           stdin=subprocess.PIPE)
    fi = 0
    t_shot = 0.0
    rnd = random.Random(7)
    for s in shots:
        n = int(round((t_shot + s["dur"]) * FPS)) - int(round(t_shot * FPS))
        for k, arr in enumerate(decode_shot(s, n, ww, wh, aspect)):
            t = fi / FPS
            # zoom: punch-in kick on the cut, settles over 0.25 s
            zoom = 1.0
            if s.get("punch", True):
                e = min(k / (0.25 * FPS), 1.0)
                zoom = 1.0 + 0.09 * (1 - e) ** 2
            zoom *= 1 + 0.03 * k / max(n, 1)  # slow drift
            cw, chh = ww / (zoom * 1.1), wh / (zoom * 1.1)
            cx, cy = ww / 2, wh / 2
            if s.get("shake") or any(abs(t - st) < 0.25 for st in shake_at):
                cx += rnd.uniform(-14, 14)
                cy += rnd.uniform(-14, 14)
            box = (cx - cw / 2, cy - chh / 2, cx + cw / 2, cy + chh / 2)
            frame = Image.fromarray(arr).resize((CW, CH), Image.LANCZOS, box=box)
            a = vignette(np.asarray(frame).astype(np.float32))
            frame = Image.fromarray(a).convert("RGBA")
            if letterbox and letterbox[0] <= t < letterbox[1]:
                d = ImageDraw.Draw(frame)
                d.rectangle([0, 0, CW, letterbox[2]], fill=(0, 0, 0, 255))
                d.rectangle([0, CH - letterbox[2], CW, CH], fill=(0, 0, 0, 255))
            for tt, img in tblocks:
                if tt["t0"] <= t < tt["t1"]:
                    im = img
                    if tt.get("pop", True):
                        age = (t - tt["t0"]) * FPS
                        sc = 1 + 0.25 * max(0, 1 - age / 5) ** 2
                        if sc > 1.001:
                            im = img.resize((int(img.width * sc), int(img.height * sc)), Image.LANCZOS)
                    frame.alpha_composite(im, (int((CW - im.width) / 2), int(tt["y"] - im.height / 2)))
            for ft in flashes:
                if 0 <= t - ft < 5 / FPS:
                    al = int(230 * (1 - (t - ft) * FPS / 5))
                    frame.alpha_composite(Image.new("RGBA", (CW, CH), (255, 255, 255, al)))
            out_im = frame.convert("RGB")
            if rotated:
                out_im = out_im.transpose(Image.ROTATE_270)
            enc.stdin.write(out_im.tobytes())
            fi += 1
        t_shot += s["dur"]
    enc.stdin.close()
    enc.wait()
    print("wrote", out, fi, "frames", f"{fi / FPS:.2f}s")

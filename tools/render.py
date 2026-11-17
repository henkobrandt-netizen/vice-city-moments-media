import subprocess, sys, os, glob, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
FONT = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
SHOTS = {os.path.basename(p)[:-4]: p for p in glob.glob("shots/**/*.jpg", recursive=True)}
CLIPS = {os.path.basename(p)[:-4]: p for p in glob.glob("videos/*.mp4")}
YELLOW = (255, 214, 10)
PINK = (255, 92, 190)

_img_cache = {}


def load_image(name):
    if name not in _img_cache:
        _img_cache[name] = Image.open(SHOTS[name]).convert("RGB")
    return _img_cache[name]


def load_clip(name, start=0.0, dur=None, bh=2266):
    probe = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                            "stream=width,height", "-of", "csv=p=0", CLIPS[name]],
                           capture_output=True, text=True).stdout.strip().split(",")
    sw, sh = int(probe[0]), int(probe[1])
    bw = int(sw * bh / sh) // 2 * 2
    cmd = ["ffmpeg", "-v", "error", "-ss", str(start), "-i", CLIPS[name]]
    if dur:
        cmd += ["-t", str(dur)]
    cmd += ["-vf", f"scale={bw}:{bh},setsar=1,fps={FPS}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    n = len(raw) // (bw * bh * 3)
    arr = np.frombuffer(raw[: n * bw * bh * 3], np.uint8).reshape(n, bh, bw, 3)
    return [Image.fromarray(a) for a in arr]


MAX_UPSCALE = 1.8


def crop_vertical(src, xc, z, yc=0.5):
    """Crop a 9:16 window from src at horizontal centre xc (0-1), zoom z (>=1).
    Zoom is capped so the crop is never stretched more than MAX_UPSCALE (keeps it sharp)."""
    ch = max(src.height / z, H / MAX_UPSCALE)
    cw = ch * 9 / 16
    if cw > src.width:
        cw = src.width
        ch = cw * 16 / 9
    x0 = min(max(xc * src.width - cw / 2, 0), src.width - cw)
    y0 = min(max(yc * src.height - ch / 2, 0), src.height - ch)
    out = src.resize((W, H), Image.LANCZOS, box=(x0, y0, x0 + cw, y0 + ch))
    if ch < H * 0.98:
        out = out.filter(ImageFilter.UnsharpMask(radius=1.6, percent=70, threshold=2))
    return out


def fit_vertical(src, z):
    """Full frame on a blurred, zoomed background."""
    bg = crop_vertical(src, 0.5, 1.0).filter(ImageFilter.GaussianBlur(40))
    bg = Image.eval(bg, lambda v: int(v * 0.55))
    fw = int(W * 1.0 * z)
    fh = int(src.height * fw / src.width)
    fg = src.resize((fw, fh), Image.BILINEAR)
    bg.paste(fg, ((W - fw) // 2, (H - fh) // 2))
    return bg


def text_block(lines, size=110, color=(255, 255, 255), stroke=12, max_w=940):
    """lines: list of (text, color or None). Returns RGBA image."""
    rendered = []
    for txt, col in lines:
        s = size
        font = ImageFont.truetype(FONT, s)
        while font.getlength(txt) > max_w and s > 40:
            s -= 4
            font = ImageFont.truetype(FONT, s)
        rendered.append((txt, col or color, font, s))
    pad = stroke * 2 + 10
    heights = [int(s * 1.12) for *_, s in rendered]
    bw = max_w + pad * 2
    bh = sum(heights) + pad * 2
    img = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    shadow = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    d, ds = ImageDraw.Draw(img), ImageDraw.Draw(shadow)
    y = pad
    for (txt, col, font, s), lh in zip(rendered, heights):
        tw = font.getlength(txt)
        x = (bw - tw) / 2
        ds.text((x + 6, y + 8), txt, font=font, fill=(0, 0, 0, 160), stroke_width=stroke, stroke_fill=(0, 0, 0, 160))
        d.text((x, y), txt, font=font, fill=col, stroke_width=stroke, stroke_fill=(0, 0, 0))
        y += lh
    shadow = shadow.filter(ImageFilter.GaussianBlur(8))
    return Image.alpha_composite(shadow, img)


def build(segments, texts, out, flashes=(), shapes=(), overlay=None, grade=None):
    """segments: dicts {img|clip, xc, dur, z0, z1, fit, punch}
    texts: dicts {t0, t1, lines, size, y (centre, px), pop}"""
    total = sum(s["dur"] for s in segments)
    nframes = int(round(total * FPS))
    tex = []
    for t in texts:
        im = text_block(t["lines"], t.get("size", 110))
        tex.append((t, im))
    enc = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
         "-i", "-", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-shortest",
         "-c:v", "libx264", "-preset", "medium", "-crf", "15", "-profile:v", "high", "-tune", "film", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", out],
        stdin=subprocess.PIPE)
    seg_start = 0.0
    fi = 0
    flash_frames = set()
    for ft in flashes:
        f0 = int(round(ft * FPS))
        flash_frames.update({f0: 1.0, f0 + 1: 0.55, f0 + 2: 0.2}.keys())
    flash_alpha = {}
    for ft in flashes:
        f0 = int(round(ft * FPS))
        for k, a in enumerate((0.85, 0.5, 0.2)):
            flash_alpha[f0 + k] = a
    for s in segments:
        n = int(round((seg_start + s["dur"]) * FPS)) - int(round(seg_start * FPS))
        frames = None
        if "clip" in s:
            frames = load_clip(s["clip"], s.get("start", 0), s.get("cdur"), s.get("clip_h", 2266))
            if s.get("pingpong"):
                frames = frames + frames[::-1]
        for k in range(n):
            p = k / max(n - 1, 1)
            z = s.get("z0", 1.0) + (s.get("z1", 1.08) - s.get("z0", 1.0)) * p
            if s.get("punch", True) and k < 6:
                z *= 1 + 0.10 * (1 - k / 6) ** 2
            if frames is not None:
                src = frames[min(int(k * len(frames) / n * s.get("speed", 1.0)), len(frames) - 1)] \
                    if not s.get("loop") else frames[k % len(frames)]
            else:
                src = load_image(s["img"])
            xc = s.get("xc", 0.5)
            if "x1" in s:
                xc = xc + (s["x1"] - xc) * p
            yc = s.get("yc", 0.5)
            if "y1" in s:
                yc = yc + (s["y1"] - yc) * p
            if "ease" in s:
                e = p * p * (3 - 2 * p)
                z = s.get("z0", 1.0) + (s.get("z1", 1.08) - s.get("z0", 1.0)) * e
                xc = s.get("xc", 0.5) + (s.get("x1", s.get("xc", 0.5)) - s.get("xc", 0.5)) * e
                yc = s.get("yc", 0.5) + (s.get("y1", s.get("yc", 0.5)) - s.get("yc", 0.5)) * e
            frame = fit_vertical(src, z) if s.get("fit") else crop_vertical(src, xc, z, yc)
            t = fi / FPS
            if grade:
                frame = grade(frame, t)
            frame = frame.convert("RGBA")
            if overlay:
                overlay(frame, t)
            for td, im in tex:
                if td["t0"] <= t < td["t1"]:
                    age = (t - td["t0"]) * FPS
                    o = im
                    if td.get("pop", True) and age < 5:
                        sc = 1 + 0.35 * (1 - age / 5) ** 2
                        o = im.resize((int(im.width * sc), int(im.height * sc)), Image.BILINEAR)
                    x = (W - o.width) // 2
                    y = int(td.get("y", 560) - o.height / 2)
                    frame.alpha_composite(o, (x, max(y, 0)))
            if shapes:
                d = ImageDraw.Draw(frame)
                for sh in shapes:
                    if sh["t0"] <= t < sh["t1"]:
                        grow = min(1.0, (t - sh["t0"]) * FPS / 6)
                        col = sh.get("color", (255, 214, 10))
                        if sh["type"] == "circle":
                            r = sh["r"] * (1.6 - 0.6 * grow)
                            for w in range(16):
                                d.ellipse([sh["cx"] - r - w, sh["cy"] - r - w, sh["cx"] + r + w, sh["cy"] + r + w], outline=col + (255,))
                        else:
                            hw, hh = sh["w"] / 2 * (1.3 - 0.3 * grow), sh["h"] / 2 * (1.3 - 0.3 * grow)
                            d.rectangle([sh["cx"] - hw, sh["cy"] - hh, sh["cx"] + hw, sh["cy"] + hh], outline=col + (255,), width=12)
            frame = frame.convert("RGB")
            if fi in flash_alpha:
                frame = Image.blend(frame, Image.new("RGB", (W, H), (255, 255, 255)), flash_alpha[fi])
            enc.stdin.write(frame.tobytes())
            fi += 1
        seg_start += s["dur"]
    enc.stdin.close()
    enc.wait()
    print("wrote", out, fi, "frames")

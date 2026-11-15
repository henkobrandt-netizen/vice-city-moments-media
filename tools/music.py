"""Original synthwave backing track (royalty-free, generated from scratch)."""
import sys
import numpy as np
from scipy.signal import butter, lfilter, sosfilt
import wave

SR = 44100
rng = np.random.default_rng(7)


def lp(x, fc, order=2):
    sos = butter(order, min(fc, SR / 2 - 100) / (SR / 2), "low", output="sos")
    return sosfilt(sos, x)


def hp(x, fc, order=2):
    sos = butter(order, fc / (SR / 2), "high", output="sos")
    return sosfilt(sos, x)


def bp(x, lo, hi):
    sos = butter(2, [lo / (SR / 2), hi / (SR / 2)], "band", output="sos")
    return sosfilt(sos, x)


def saw(f, n, phase=0.0):
    t = np.arange(n) / SR
    return 2 * ((f * t + phase) % 1.0) - 1


def note_hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def env(n, a=0.005, d=0.1, s=0.0, r=0.05, hold=None):
    e = np.zeros(n)
    ai = max(int(a * SR), 1)
    di = max(int(d * SR), 1)
    e[:ai] = np.linspace(0, 1, ai)[: n]
    end = min(ai + di, n)
    if end > ai:
        e[ai:end] = np.linspace(1, s, end - ai + 0)[: end - ai] if di else s
    e[end:] = s
    if r and s > 0:
        ri = min(int(r * SR), n)
        e[n - ri:] *= np.linspace(1, 0, ri)
    return e


def add(buf, sig, start):
    i = int(start * SR)
    if i >= len(buf):
        return
    j = min(len(buf), i + len(sig))
    buf[i:j] += sig[: j - i]


def kick():
    n = int(0.45 * SR)
    t = np.arange(n) / SR
    f = 45 + 110 * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) * np.exp(-t * 7)
    click = hp(rng.standard_normal(n), 2000) * np.exp(-t * 300) * 0.3
    return np.tanh(1.8 * (s + click)) * 0.9


def snare():
    n = int(0.3 * SR)
    t = np.arange(n) / SR
    noise = bp(rng.standard_normal(n), 1200, 8000) * np.exp(-t * 16)
    tone = np.sin(2 * np.pi * 185 * t) * np.exp(-t * 25)
    return (noise * 0.7 + tone * 0.5) * 0.8


def hat(open_=False):
    n = int((0.18 if open_ else 0.05) * SR)
    t = np.arange(n) / SR
    return hp(rng.standard_normal(n), 7000) * np.exp(-t * (18 if open_ else 90)) * 0.25


def crash():
    n = int(2.0 * SR)
    t = np.arange(n) / SR
    return hp(rng.standard_normal(n), 4000) * np.exp(-t * 2.2) * 0.35


def chord_pad(notes, dur, cutoff=2200):
    n = int(dur * SR)
    s = np.zeros(n)
    for m in notes:
        for det in (-0.12, 0.0, 0.12):
            s += saw(note_hz(m + det), n, rng.random())
    s = lp(s / (len(notes) * 3), cutoff)
    return s * env(n, a=0.25, d=0.2, s=0.8, r=0.3)


def bass_note(m, dur):
    n = int(dur * SR)
    s = saw(note_hz(m), n) + 0.5 * saw(note_hz(m - 12), n)
    s = lp(s, 600)
    return s * env(n, a=0.004, d=dur * 0.6, s=0.3, r=0.03) * 0.75


def arp_note(m, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = np.sign(np.sin(2 * np.pi * note_hz(m) * t)) * 0.5 + saw(note_hz(m), n) * 0.5
    s = lp(s, 3500)
    return s * env(n, a=0.002, d=dur * 0.9, s=0.0) * 0.22


def riser(dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    noise = rng.standard_normal(n)
    out = np.zeros(n)
    seg = int(0.05 * SR)
    for k in range(0, n, seg):
        fc = 400 + 7000 * (k / n) ** 2
        out[k:k + seg] = bp(noise[k:k + seg + 2000], fc * 0.7, fc * 1.3)[: len(out[k:k + seg])]
    return out * np.linspace(0.05, 0.6, n)


def make_track(total, drop, accents=(), bpm=118, out="track.wav", shift=0):
    buf = np.zeros(int(total * SR) + SR)
    beat = 60 / bpm
    bar = 4 * beat
    # A minor: Am - F - C - G
    prog = [(57, [69, 72, 76]), (53, [65, 69, 72]), (48, [64, 67, 72]), (55, [62, 67, 71])]
    prog = [(r + shift, [m + shift for m in ch]) for r, ch in prog]
    arp_pat = [0, 1, 2, 1, 2, 3, 2, 1]

    # intro (before drop): filtered pad + riser + soft arp
    if drop > 0:
        add(buf, chord_pad([m + shift for m in (69, 72, 76, 57)], drop, cutoff=900) * 0.6, 0)
        add(buf, riser(drop), 0)
        k = 0
        t = 0.0
        while t < drop - beat / 2:
            notes = prog[0][1] + [prog[0][1][0] + 12]
            add(buf, arp_note(notes[arp_pat[k % 8]], beat / 2) * 0.6, t)
            t += beat / 2
            k += 1

    # main section
    t0 = drop
    nb = int(np.ceil((total - t0) / bar)) + 1
    for b in range(nb):
        root, ch = prog[b % 4]
        bt = t0 + b * bar
        if bt >= total:
            break
        add(buf, chord_pad(ch, bar, cutoff=2600) * 0.45, bt)
        for q in range(8):
            add(buf, bass_note(root - 12 + (12 if q % 2 else 0), beat / 2), bt + q * beat / 2)
        notes = ch + [ch[0] + 12]
        for q in range(16):
            add(buf, arp_note(notes[arp_pat[q % 8]] + 12, beat / 4), bt + q * beat / 4)
        for q in range(4):
            add(buf, kick(), bt + q * beat)
            if q in (1, 3):
                add(buf, snare(), bt + q * beat)
            add(buf, hat(), bt + q * beat + beat / 2)
            add(buf, hat(), bt + q * beat + beat / 4 * 3)
    add(buf, crash(), drop)
    for a in accents:
        add(buf, crash(), a)
        add(buf, kick(), a)

    buf = buf[: int(total * SR)]
    # sidechain-ish pump on everything but kick is skipped for simplicity; master
    buf = np.tanh(buf * 1.3)
    buf /= np.max(np.abs(buf)) + 1e-9
    buf *= 0.89
    fade = int(0.35 * SR)
    buf[-fade:] *= np.linspace(1, 0, fade)
    st = np.stack([buf, np.roll(buf, 220) * 0.98], axis=1)
    pcm = (st * 32767).astype(np.int16)
    with wave.open(out, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print("wrote", out)


if __name__ == "__main__":
    total, drop = float(sys.argv[1]), float(sys.argv[2])
    bpm, shift = float(sys.argv[4]), int(sys.argv[5])
    accents = [float(a) for a in sys.argv[6:]]
    make_track(total, drop, accents, bpm=bpm, out=sys.argv[3], shift=shift)

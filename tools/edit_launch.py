"""EDIT 1 – 'GTA 6 IS FINALLY HERE' launch-day edit.
TikTok sound: Flower In A Hurricane (Justice, Tame Impala, SZA, King Gizzard) – beat 0.9502 s, first hit 0.99 s."""
import sys
from clipedit import build, YELLOW

L, T2, T1 = "trailers/launch.mp4", "trailers/t2.mp4", "trailers/t1.mp4"
B = 0.9502
first = 0.99


def S(src, start, xc=0.5, **k):
    return dict(src=src, start=start, xc=xc, **k)


whole = [S(T1, 35.8, 0.5, punch=False), S(L, 25.8, 0.27), S(L, 46.4, 0.55), S(T1, 23.4, 0.42),
         S(L, 54.6, 0.52), S(L, 27.4, 0.6), S(T2, 138.15, 0.72), S(L, 72.15, 0.4)]
half = [S(L, 69.0, 0.45), S(T2, 118.0, 0.7), S(T1, 65.7, 0.3), S(T2, 140.3, 0.42),
        S(L, 32.15, 0.45), S(T1, 70.6, 0.45), S(L, 34.5, 0.5), S(T2, 142.0, 0.5)]
ends = [S(L, 66.45, 0.5, speed=0.79), S(T1, 31.0, 0.5, punch=False, speed=0.84)]

shots = []
whole[0]["dur"] = first
for s in whole[1:]:
    s["dur"] = B
for s in half:
    s["dur"] = B / 2
for s in ends:
    s["dur"] = 2 * B
shots = whole + half + ends
t_half = first + 7 * B
t_end1 = t_half + 8 * B / 2
t_end2 = t_end1 + 2 * B
T = t_end2 + 2 * B

texts = [
    dict(t0=0, t1=first + B, lines=[("GTA 6 IS", None), ("FINALLY HERE", YELLOW)], size=130, y=760),
    dict(t0=t_end1, t1=t_end2, lines=[("SEE YOU IN", None), ("VICE CITY", YELLOW)], size=140, y=760),
    dict(t0=t_end2, t1=T + 1, lines=[("WHERE ARE YOU", None), ("GOING FIRST?", YELLOW)], size=120, y=760),
]
flashes = [t_half, t_end1]

if __name__ == "__main__":
    print("length", round(T, 2))
    build(shots, texts, sys.argv[1] if len(sys.argv) > 1 else "out/07_launch_edit.mp4", flashes=flashes)

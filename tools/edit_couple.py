"""EDIT 3 – Jason & Lucia couple edit. TikTok sound: Se Me Nota (Agarrame) – Chimbala & Omega.
Beat 0.9354 s, first hit 0.99 s."""
import sys
from clipedit import build, YELLOW

L, T2, T1 = "trailers/launch.mp4", "trailers/t2.mp4", "trailers/t1.mp4"
B = 0.9354
first = 0.99


def S(src, start, xc=0.5, dur=B, **k):
    return dict(src=src, start=start, xc=xc, dur=dur, **k)


shots = [S(L, 25.8, 0.27, dur=first, punch=False),
         S(T2, 98.6, 0.5), S(T2, 79.6, 0.45), S(T1, 62.6, 0.55), S(T1, 60.6, 0.4),
         S(L, 62.6, 0.5), S(T2, 88.3, 0.45), S(L, 39.9, 0.57),
         S(T1, 68.8, 0.25, dur=B / 2), S(L, 72.15, 0.4, dur=B / 2), S(T2, 118.0, 0.7, dur=B / 2), S(L, 69.0, 0.45, dur=B / 2),
         S(T1, 72.9, 0.5), S(T2, 97.72, 0.45, speed=0.78),
         S(L, 66.45, 0.5, dur=2 * B, speed=0.75, punch=False)]
t_action = first + 7 * B
t_end = t_action + 2 * B + 2 * B
T = t_end + 2 * B

texts = [
    dict(t0=0, t1=first + B, lines=[("POV: YOU FOUND YOUR", None), ("PARTNER IN CRIME", YELLOW)], size=110, y=760),
    dict(t0=t_action, t1=t_action + 2 * B, lines=[("SHE'S DOWN", None), ("FOR ANYTHING", YELLOW)], size=120, y=760),
    dict(t0=t_end, t1=T + 1, lines=[("TAG YOUR", None), ("PARTNER IN CRIME", YELLOW)], size=120, y=760),
]
flashes = [t_action, t_end]

if __name__ == "__main__":
    print("length", round(T, 2))
    build(shots, texts, sys.argv[1] if len(sys.argv) > 1 else "out/09_couple_edit.mp4", flashes=flashes)

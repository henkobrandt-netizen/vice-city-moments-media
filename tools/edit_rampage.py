"""EDIT 2 – phonk action edit. TikTok sound: RAMPAGE - SLOWED (ZMAJOR & Lurk & SEKIMANE).
Beat 0.5576 s, drop at 5.58 s, bars every 2.23 s."""
import sys
from clipedit import build, YELLOW

L, T2, T1 = "trailers/launch.mp4", "trailers/t2.mp4", "trailers/t1.mp4"
B = 0.5576
DROP = 5.58


def S(src, start, xc=0.5, **k):
    return dict(src=src, start=start, xc=xc, **k)


intro = [S(L, 2.2, 0.62, punch=False, speed=0.75, dur=2.79), S(T1, 5.0, 0.5, punch=False, speed=0.54, dur=2.79)]
drop = [S(L, 72.15, 0.4), S(L, 46.4, 0.55), S(T2, 118.0, 0.7), S(T1, 65.7, 0.3),
        S(L, 69.0, 0.45), S(L, 13.6, 0.45), S(L, 32.15, 0.45), S(T1, 68.8, 0.25),
        S(T2, 46.0, 0.5), S(L, 33.1, 0.5), S(T1, 70.6, 0.45), S(T2, 140.3, 0.42),
        S(L, 38.4, 0.5), S(T2, 20.6, 0.5), S(L, 25.8, 0.27), S(T2, 142.0, 0.5)]
for s in drop:
    s["dur"] = B
end = [S(L, 39.9, 0.57, punch=True, dur=4 * B)]
shots = intro + drop + end
T_END = DROP + 16 * B
T = T_END + 4 * B

texts = [
    dict(t0=0, t1=2.79, lines=[("THEY SAID IT WOULD", None), ("NEVER COME OUT", YELLOW)], size=110, y=760, pop=False),
    dict(t0=2.79, t1=DROP, lines=[("13 YEARS LATER...", None)], size=110, y=760, pop=False),
    dict(t0=DROP, t1=DROP + 4 * B, lines=[("GTA 6", YELLOW), ("IS HERE", None)], size=170, y=760),
    dict(t0=T_END, t1=T + 1, lines=[("WHO'S YOUR", None), ("GETAWAY DRIVER?", YELLOW)], size=120, y=760),
]
flashes = [DROP + k * 4 * B for k in range(5)]

if __name__ == "__main__":
    print("length", round(T, 2))
    build(shots, texts, sys.argv[1] if len(sys.argv) > 1 else "out/08_rampage_edit.mp4",
          flashes=flashes, letterbox=(0, DROP, 330), shake_at=[DROP])

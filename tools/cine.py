"""Cinematic sideways versions of the three edits (style learned from the owner's saved edits:
full landscape frame turned sideways, almost no text, grade + flashes on the beat).
Usage: python3 cine.py launch|rampage|couple"""
import sys
from clipedit import build

WHITE = None
name = sys.argv[1]
if name == "launch":
    import edit_launch as e
    texts = [
        dict(t0=0.15, t1=e.first + e.B, lines=[("IT'S TIME.", WHITE)], size=72, y=900, pop=False),
        dict(t0=e.t_end1, t1=e.T + 1, lines=[("WELCOME TO VICE CITY", WHITE)], size=72, y=900, pop=False),
    ]
    build(e.shots, texts, "out/07c_launch_cine.mp4", flashes=e.flashes, rotated=True, text_max_w=1500)
elif name == "rampage":
    import edit_rampage as e
    texts = [
        dict(t0=0.3, t1=2.79, lines=[("THEY SAID IT WOULD NEVER COME OUT", WHITE)], size=58, y=920, pop=False),
        dict(t0=2.79, t1=e.DROP, lines=[("13 YEARS LATER.", WHITE)], size=58, y=920, pop=False),
        dict(t0=e.DROP, t1=e.DROP + 4 * e.B, lines=[("GTA VI", WHITE)], size=150, y=540),
    ]
    build(e.shots, texts, "out/08c_rampage_cine.mp4", flashes=e.flashes, letterbox=(0, e.DROP, 140),
          shake_at=[e.DROP], rotated=True, text_max_w=1500)
elif name == "couple":
    import edit_couple as e
    texts = [
        dict(t0=0.15, t1=e.first + e.B, lines=[("FIND YOUR LUCIA.", WHITE)], size=72, y=900, pop=False),
        dict(t0=e.t_end, t1=e.T + 1, lines=[("PARTNERS IN CRIME.", WHITE)], size=72, y=900, pop=False),
    ]
    build(e.shots, texts, "out/09c_couple_cine.mp4", flashes=e.flashes, rotated=True, text_max_w=1500)

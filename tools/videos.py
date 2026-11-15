import sys
from render import build, YELLOW, PINK

OUT = "/home/claude/src/out"


def countdown(days_label, small_label, fname, top="GTA 6 COMES OUT IN"):
    segs = [
        dict(img="Jason_and_Lucia_01", xc=0.47, dur=2.2, z0=1.0, z1=1.14, punch=False),
        dict(clip="Jason_Duval_Video_Clip", xc=0.55, dur=1.0),
        dict(clip="Lucia_Caminos_Video_Clip", xc=0.62, dur=1.2),
        dict(img="Jason_and_Lucia_09", xc=0.62, dur=0.7),
        dict(img="Vice_City_17", xc=0.45, dur=0.7),
        dict(clip="Real_Dimez_Video_Clip", xc=0.5, dur=0.9),
        dict(img="Jason_and_Lucia_04", xc=0.3, dur=0.7),
        dict(img="Vice_City_11", xc=0.25, dur=0.7),
        dict(clip="DreQuan_Priest_Video_Clip", xc=0.5, dur=0.9),
        dict(img="Jason_and_Lucia_19", xc=0.62, dur=0.7),
        dict(img="Vice_City_27", xc=0.5, dur=0.7),
        dict(img="Vice_City_01", xc=0.2, dur=1.0),
        dict(clip="GTAVI_Official_Cover_Art_Landscape", start=12.0, cdur=3.0, fit=True, clip_h=1400, dur=2.8, z0=2.3, z1=2.45, punch=False),
    ]
    end = sum(s["dur"] for s in segs)
    texts = [
        dict(t0=0, t1=2.2, lines=[(top, None)], size=86, y=1000, pop=False),
        dict(t0=0, t1=2.2, lines=[(days_label, YELLOW)], size=230, y=1180),
        dict(t0=2.2, t1=end - 2.8, lines=[(small_label, YELLOW)], size=72, y=330, pop=False),
        dict(t0=end - 2.8, t1=end, lines=[("NOV 19", YELLOW)], size=200, y=380),
        dict(t0=end - 2.8, t1=end, lines=[("BUYING IT DAY ONE?", None), ("YES OR NO", None)], size=80, y=1430),
    ]
    build(segs, texts, f"{OUT}/{fname}", flashes=[2.2, end - 2.8])


def couple():
    segs = [
        dict(img="Jason_and_Lucia_03", xc=0.33, dur=2.6, z0=1.0, z1=1.12, punch=False),
        dict(img="Jason_and_Lucia_06", xc=0.62, dur=1.2, z0=1.05, z1=1.15),
        dict(img="Jason_and_Lucia_19", xc=0.6, dur=0.7),
        dict(img="Jason_and_Lucia_02", xc=0.45, dur=0.7),
        dict(img="Jason_and_Lucia_09", xc=0.58, dur=0.7),
        dict(clip="Lucia_Caminos_Video_Clip", xc=0.62, dur=1.3),
        dict(img="Jason_and_Lucia_04", xc=0.3, dur=0.7),
        dict(img="Jason_and_Lucia_17", xc=0.27, dur=0.7),
        dict(img="Jason_and_Lucia_08", xc=0.5, dur=0.8),
        dict(clip="Jason_Duval_Video_Clip", xc=0.55, dur=1.0),
        dict(img="Jason_and_Lucia_13", xc=0.5, dur=2.6, z0=1.0, z1=1.1, punch=False),
    ]
    end = sum(s["dur"] for s in segs)
    texts = [
        dict(t0=0, t1=2.6, lines=[("SHE SAID GTA 6 WAS", None), ('"JUST A GAME"', YELLOW)], size=96, y=560),
        dict(t0=2.6, t1=3.8, lines=[("3 HOURS LATER:", YELLOW)], size=110, y=600),
        dict(t0=end - 2.6, t1=end, lines=[("PARTNERS IN CRIME", PINK)], size=100, y=420),
        dict(t0=end - 2.6, t1=end, lines=[("TAG YOUR PLAYER 2", None)], size=84, y=1430),
    ]
    build(segs, texts, f"{OUT}/02_partners_in_crime.mp4", flashes=[2.6, end - 2.6])


def notmiami():
    segs = [
        dict(img="Vice_City_10", xc=0.38, dur=2.0, z0=1.0, z1=1.12, punch=False),
        dict(img="Vice_City_15", xc=0.55, dur=1.4, z0=1.0, z1=1.1),
        dict(img="Leonida_Keys_01", xc=0.55, dur=0.8),
        dict(img="Vice_City_26", xc=0.45, dur=0.8),
        dict(img="Leonida_Keys_05", xc=0.5, dur=0.8),
        dict(img="Vice_City_11", xc=0.25, dur=0.8),
        dict(img="Grassrivers_05", xc=0.5, dur=0.8),
        dict(img="Mount_Kalaga_National_Park_04", xc=0.55, dur=0.8),
        dict(img="Leonida_Keys_04", xc=0.5, dur=0.8),
        dict(img="Vice_City_03", xc=0.5, dur=0.8),
        dict(img="Port_Gellhorn_06", xc=0.45, dur=0.8),
        dict(img="Vice_City_27", xc=0.5, dur=2.6, z0=1.0, z1=1.1, punch=False),
    ]
    end = sum(s["dur"] for s in segs)
    texts = [
        dict(t0=0, t1=2.0, lines=[("THIS ISN'T MIAMI.", None)], size=110, y=600),
        dict(t0=2.0, t1=3.4, lines=[("IT'S GTA 6.", YELLOW)], size=150, y=600),
        dict(t0=3.4, t1=end - 2.6, lines=[("ALL OF THIS IS IN-GAME", None)], size=62, y=330, pop=False),
        dict(t0=end - 2.6, t1=end, lines=[("WHERE ARE YOU", None), ("GOING FIRST?", YELLOW)], size=100, y=560),
    ]
    build(segs, texts, f"{OUT}/03_this_isnt_miami.mp4", flashes=[2.0])


if __name__ == "__main__":
    import os
    os.makedirs(OUT, exist_ok=True)
    which = sys.argv[1]
    if which == "cd4":
        countdown("4 DAYS", "4 DAYS LEFT", "01a_countdown_4_days.mp4")
    elif which == "cd3":
        countdown("3 DAYS", "3 DAYS LEFT", "01b_countdown_3_days.mp4")
    elif which == "cd2":
        countdown("2 DAYS", "2 DAYS LEFT", "01c_countdown_2_days.mp4")
    elif which == "cd1":
        countdown("TOMORROW", "1 DAY LEFT", "01d_countdown_tomorrow.mp4", top="GTA 6 COMES OUT")
    elif which == "couple":
        couple()
    elif which == "miami":
        notmiami()

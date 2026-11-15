from render import build, YELLOW, PINK
segs = [
    dict(img="Vice_City_06", xc=0.234, yc=0.529, z0=1.9, z1=2.0, dur=2.4, punch=False),
    dict(img="Vice_City_06", xc=0.234, yc=0.529, x1=0.17, y1=0.5, z0=2.0, z1=1.25, ease=True, dur=2.2, punch=False),
    dict(img="Vice_City_22", xc=0.55, yc=0.5, x1=0.7675, y1=0.141, z0=1.0, z1=2.0, ease=True, dur=3.6, punch=False),
    dict(img="Vice_City_22", xc=0.7675, yc=0.141, z0=2.0, z1=2.0, dur=2.6, punch=False),
    dict(img="Vice_City_27", xc=0.5, z0=1.0, z1=1.1, dur=2.2),
]
texts = [
    dict(t0=0, t1=2.4, lines=[("NOBODY NOTICED", None), ("THIS IN GTA 6", YELLOW)], size=120, y=380),
    dict(t0=2.4, t1=4.6, lines=[("IT SAYS", None), ('"VICE BEACH POLICE"', YELLOW)], size=96, y=380),
    dict(t0=4.6, t1=7.4, lines=[("#2: THE RICARDO", None), ("TIRES SIGN...", YELLOW)], size=100, y=380),
    dict(t0=7.4, t1=10.8, lines=[("HAS A PIGEON", None), ("LIVING IN IT", YELLOW)], size=120, y=1250),
    dict(t0=10.8, t1=13.0, lines=[("WHAT ELSE", None), ("DID YOU SPOT?", YELLOW)], size=120, y=700),
]
shapes = [
    dict(type="box", cx=707, cy=960, w=560, h=130, t0=0.3, t1=2.4),
    dict(type="circle", cx=540, cy=540, r=105, t0=7.4, t1=10.8, color=YELLOW),
]
build(segs, texts, "out/04_did_you_notice.mp4", flashes=[2.4, 4.6, 10.8], shapes=shapes)

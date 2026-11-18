"""Build the Build Bill subscribed calendar feed.

Edit calendar/build_bill_events.json (add/remove events), then run:
    python3 calendar/build_bill_ics.py
and commit + push calendar/build-bill.ics. Subscribed phones pick it up (hourly hint).

Event fields: id (stable, unique), start "YYYY-MM-DDTHH:MM" (SAST), mins,
title, notes, optional url, info (true = shows as free, no alert),
optional alarm_min (alert this many minutes before; to-dos default 0).
"""
import json, os, hashlib
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
events = json.load(open(os.path.join(HERE, "build_bill_events.json")))

def esc(s):
    return s.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")

def fold(line):
    b = line.encode("utf-8"); out = []
    while len(b) > 74:
        cut = 74
        while (b[cut] & 0xC0) == 0x80: cut -= 1
        out.append(b[:cut].decode()); b = b" " + b[cut:]
    out.append(b.decode()); return "\r\n".join(out)

stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
L = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//The Build Bill//Schedule//EN", "CALSCALE:GREGORIAN",
     "X-WR-CALNAME:Build Bill", "X-WR-TIMEZONE:Africa/Johannesburg",
     "REFRESH-INTERVAL;VALUE=DURATION:PT1H", "X-PUBLISHED-TTL:PT1H",
     "BEGIN:VTIMEZONE", "TZID:Africa/Johannesburg", "BEGIN:STANDARD", "DTSTART:19700101T000000",
     "TZOFFSETFROM:+0200", "TZOFFSETTO:+0200", "TZNAME:SAST", "END:STANDARD", "END:VTIMEZONE"]
for e in sorted(events, key=lambda e: e["start"]):
    st = datetime.strptime(e["start"], "%Y-%m-%dT%H:%M"); en = st + timedelta(minutes=e.get("mins", 15))
    L += ["BEGIN:VEVENT", "UID:" + hashlib.md5(e["id"].encode()).hexdigest() + "@buildbill", "DTSTAMP:" + stamp,
          "DTSTART;TZID=Africa/Johannesburg:" + st.strftime("%Y%m%dT%H%M%S"),
          "DTEND;TZID=Africa/Johannesburg:" + en.strftime("%Y%m%dT%H%M%S"),
          "SUMMARY:" + esc(e["title"]), "DESCRIPTION:" + esc(e["notes"] + ("\n" + e["url"] if e.get("url") else ""))]
    if e.get("url"): L.append("URL:" + e["url"])
    L.append("TRANSP:TRANSPARENT" if e.get("info") else "TRANSP:OPAQUE")
    if not e.get("info"):
        L += ["BEGIN:VALARM", "ACTION:DISPLAY", "DESCRIPTION:" + esc(e["title"]),
              f"TRIGGER:-PT{int(e.get('alarm_min', 0))}M", "END:VALARM"]
    L.append("END:VEVENT")
L.append("END:VCALENDAR")
open(os.path.join(HERE, "build-bill.ics"), "w", newline="").write("\r\n".join(fold(l) for l in L) + "\r\n")
print(len(events), "events ->", os.path.join(HERE, "build-bill.ics"))

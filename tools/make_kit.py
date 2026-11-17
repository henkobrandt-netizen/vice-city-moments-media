"""Build the owner's TikTok posting kit + a calendar reminders file (.ics).

Usage: python3 tools/make_kit.py kit.json OUT_DIR
kit.json = {"name": "2026-11-18-edits", "posts": [
  {"file": "TT_05_days_waited_SILENT.mp4", "when": "2026-11-18 20:00",
   "sound": "Blood In Your Eyes (from GTAVI: The Album) – Tove Lo & Grand Theft Auto VI",
   "sound_url": "https://www.tiktok.com/music/...", "caption": "...", "what": "short label"}]}
Times are Africa/Johannesburg. Writes OUT_DIR/VCM_TikTok_kit_<name>.md and
OUT_DIR/VCM_TikTok_reminders_<name>.ics (one event per post, alerts 60 and 10 min before).
The .ics opens on iPhone/Mac/Windows and adds to the iCloud Calendar (Reminders can't import files)."""
import json, sys, os, uuid
from datetime import datetime, timedelta, timezone

TZ = "Africa/Johannesburg"


def esc(s):
    return s.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def fold(line):
    out, b = [], line.encode()
    while len(b) > 73:
        cut = 73
        while (b[cut] & 0xC0) == 0x80:
            cut -= 1
        out.append(b[:cut].decode())
        b = b[cut:]
    out.append(b.decode())
    return "\r\n ".join(out)


def main(cfg_path, out_dir):
    cfg = json.load(open(cfg_path))
    name, posts = cfg["name"], cfg["posts"]
    os.makedirs(out_dir, exist_ok=True)
    md = [f"# Vice City Moments – TikTok kit ({name})", "",
          "For each post: save the file → TikTok **+** → Upload → **Sounds**: search the sound, keep it starting at **0:00**,",
          "set the video's original volume to 0 → paste the caption → Post (Everyone, comments on).", ""]
    ics = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Vice City Moments//TikTok kit//EN", "CALSCALE:GREGORIAN",
           "BEGIN:VTIMEZONE", f"TZID:{TZ}", "BEGIN:STANDARD", "DTSTART:19700101T000000",
           "TZOFFSETFROM:+0200", "TZOFFSETTO:+0200", "TZNAME:SAST", "END:STANDARD", "END:VTIMEZONE"]
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    for i, p in enumerate(posts, 1):
        t = datetime.strptime(p["when"], "%Y-%m-%d %H:%M")
        md += [f"## {i}. {t:%a %d %b, %H:%M} – {p.get('what', p['file'])}",
               f"- **File:** `{p['file']}`",
               f"- **Sound:** {p['sound']}" + (f" ({p['sound_url']})" if p.get("sound_url") else ""),
               "- **Caption (copy):**", "", "```", p["caption"], "```", ""]
        desc = (f"File: {p['file']}\nSound: {p['sound']} (from 0:00, original volume 0)\n"
                + (f"{p['sound_url']}\n" if p.get("sound_url") else "") + f"Caption:\n{p['caption']}")
        ics += ["BEGIN:VEVENT", f"UID:{uuid.uuid4()}@vcm", f"DTSTAMP:{stamp}",
                f"DTSTART;TZID={TZ}:{t:%Y%m%dT%H%M%S}",
                f"DTEND;TZID={TZ}:{t + timedelta(minutes=15):%Y%m%dT%H%M%S}",
                fold("SUMMARY:" + esc(f"VCM TikTok: post {p.get('what', p['file'])}")),
                fold("DESCRIPTION:" + esc(desc))]
        for mins in (60, 10):
            ics += ["BEGIN:VALARM", "ACTION:DISPLAY", fold("DESCRIPTION:" + esc(f"Post on TikTok: {p.get('what', p['file'])}")),
                    f"TRIGGER:-PT{mins}M", "END:VALARM"]
        ics += ["END:VEVENT"]
    ics += ["END:VCALENDAR"]
    mdp = os.path.join(out_dir, f"VCM_TikTok_kit_{name}.md")
    icp = os.path.join(out_dir, f"VCM_TikTok_reminders_{name}.ics")
    open(mdp, "w").write("\n".join(md))
    open(icp, "w", newline="").write("\r\n".join(ics) + "\r\n")
    print(mdp)
    print(icp)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])

# vice-city-moments-media

Media host + editing pipeline for the **Vice City Moments** YouTube channel.

- `shorts/<batch>/` – finished vertical Shorts (with original music), fetched by vidIQ via raw.githubusercontent.com URLs.
- `tools/render.py` – 1080x1920 renderer (Ken Burns crops, punch-in cuts, hook text, flashes).
- `tools/videos.py` – edit definitions (shot lists + on-screen text) per Short.
- `tools/music.py` – original synthwave backing-track generator (royalty-free).

Source footage: official Rockstar Games GTA VI media kit (rockstargames.com/VI/media), which Rockstar offers to download and share.

## Footage
`footage/screenshots` (138 official screenshots) and `footage/clips` (9 official clips) from the Rockstar Games GTA VI media kit. `tools/render.py` expects them under `shots/` and `videos/` relative to its working directory – symlink or copy before rendering.

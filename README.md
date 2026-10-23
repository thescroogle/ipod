# Pod Classic web player (1st-gen style)
Open index.html (self-contained: CSS, JS, embedded pixel font Pixelify Sans (OFL), seed library).
Served locally: python3 -m http.server 8765 --directory /workspace/ipod-clone
Controls: drag in a circle on the wheel (mouse/touch/pen), mouse wheel/trackpad, Up/Down arrows = scroll;
center / Enter = select; menu / Esc / Backspace = back; Left/Right = prev/next (hold the ring buttons to seek); Space = play/pause.
On Now Playing: wheel = volume (overlay); center toggles scrub mode (wheel seeks).
Optional: ?am=<music.apple.com album or song URL> loads that album's previews via the iTunes lookup API.
Rebuild the seed: python3 build/fetch_data.py && python3 build/assemble.py

## v2 (Oct 2026)
- The library lives in `songs.json`: 15 playlists, 1,029 songs, 682 artists. Metadata and 30-second previews come from the public iTunes Lookup API. A track's optional `src` (full-length audio) is played instead of its preview.
- The click wheel:
  - Ignores moves shorter than 10% of the radius and moves that cut across the hub.
  - Needs 8° before it accepts a change of direction.
  - Scrolls one row per 15°.
  - Accelerates by smoothed speed, in tiers of 1, 2, 3, 5, 8, 13, 21 and 34 rows.
- Volume runs 0–100 over 1.25 turns, with 22 detent clicks across the range.
- Seeking: press center on Now Playing and the wheel scrubs. Holding |◀◀ or ▶▶| seeks in steps of 5, 10 and 20 seconds.
- Tracks crossfade over 2 seconds with equal-power curves, through WebAudio gain.
- Prev restarts the track if you are more than 3 seconds in.
- After 10 seconds idle while a track is playing, the screen returns to Now Playing.
- Every list remembers its selection. Artists starts with "All".
- Reset asks for confirmation. About shows the song and artist counts.
- Backlight options are Off, 1, 2, 3 or 5 seconds, or Always On. The default follows the color scheme.
- Hidden Brick game: hold center for 5 seconds on Settings > About.
- Preloaded track: OBSESSION by Aulani Design Lab is cued on load (`preload` in songs.json). It is visible in Now Playing and the mini player, and starts on the first play press. It never autoplays.
- Build: `OUT=. AULANI_OUT= python3 build/assemble2.py` writes `index.html` and `songs.json`.

# Pod Classic web player (1st-gen style)
Open index.html (self-contained: CSS, JS, embedded pixel font Pixelify Sans (OFL), seed library).
Served locally: python3 -m http.server 8765 --directory /workspace/ipod-clone
Controls: drag in a circle on the wheel (mouse/touch/pen), mouse wheel/trackpad, Up/Down arrows = scroll;
center / Enter = select; menu / Esc / Backspace = back; Left/Right = prev/next (hold the ring buttons to seek); Space = play/pause.
On Now Playing: wheel = volume (overlay); center toggles scrub mode (wheel seeks).
Optional: ?am=<music.apple.com album or song URL> loads that album's previews via the iTunes lookup API.
Rebuild the seed: python3 build/fetch_data.py && python3 build/assemble.py

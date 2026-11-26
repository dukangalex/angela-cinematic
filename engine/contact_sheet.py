#!/usr/bin/env python3
"""Contact sheet for visual QA: one frame per narration line, tiled and
labelled with the line number and its first words. The sheet is the fastest
way for a human (or an agent with eyes) to catch a broken layout, a tofu
glyph, or an element that fires on the wrong word — before anyone watches
the whole film.

  python3 contact_sheet.py --project my-film [--video out/draft.mp4]
Writes <project>/out/contact_sheet.jpg.
"""
import argparse, json, subprocess, sys
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--video", default="out/draft.mp4")
    ap.add_argument("--cols", type=int, default=4)
    ap.add_argument("--width", type=int, default=480, help="tile width px")
    a = ap.parse_args()

    proj = Path(a.project)
    timing = json.loads((proj / "audio" / "timing.json").read_text(encoding="utf-8"))
    segs = timing["segments"]
    video = proj / a.video
    if not video.exists():
        sys.exit(f"{video} not found — render first")
    out = proj / "out" / "contact_sheet.jpg"

    tiles = []
    with subprocess.Popen(["ffmpeg", "-v", "error", "-version"],
                          stdout=subprocess.DEVNULL):
        pass
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        for s in segs:
            t = min(s["start"] + 0.35, max(0.0, s["end"] - 0.05))
            tile = Path(td) / f"t{s['id']:02d}.png"
            label = f"{s['id']}: {s.get('caption', '')[:14]}"
            vf = (f"scale={a.width}:-2,drawtext=text='{label.replace(chr(39), '').replace(':', ' ')}'"
                  f":x=8:y=8:fontsize=22:fontcolor=white:borderw=2:bordercolor=black")
            r = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", str(video),
                                "-frames:v", "1", "-vf", vf, str(tile), "-y"])
            if r.returncode == 0 and tile.exists():
                tiles.append(tile)
        if not tiles:
            sys.exit("no frames extracted")
        rows = (len(tiles) + a.cols - 1) // a.cols
        lst = Path(td) / "list.txt"
        lst.write_text("".join(f"file '{t}'\n" for t in tiles))
        subprocess.run(["ffmpeg", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lst),
                        "-filter_complex",
                        f"tile={a.cols}x{rows}:padding=4:margin=4:color=0x222222",
                        "-frames:v", "1", str(out), "-y"], check=True)
    print(f"contact sheet: {out} ({len(tiles)} lines)")


if __name__ == "__main__":
    main()

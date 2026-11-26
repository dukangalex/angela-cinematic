#!/usr/bin/env python3
"""Scaffold a starter scene.py from a project's script.json + photos.json.

A first draft, not a film: photos pinned in a row (photos.json order), the
camera visiting each in turn, typed lines as type-on headlines, the first
big number in a line as a rolling Counter, verdict words
（属实/基本属实/夸大/不实/失败/成功） as end-of-line stamps. World units are
4K pixels, matching the engine. Author from here — it refuses to overwrite
an existing scene.py.

  python3 scaffold_scene.py --project my-film [--style infographic]
"""
import argparse, json, re, sys
from pathlib import Path

VERDICTS = ["基本属实", "属实", "夸大", "不实", "失败", "成功"]
NUM = re.compile(r"\d[\d,]*\.?\d*")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--style", default="wall")
    ap.add_argument("--out", default="scene.py")
    a = ap.parse_args()

    proj = Path(a.project)
    out = proj / a.out
    if out.exists():
        sys.exit(f"{out} exists — refusing to overwrite an authored scene")
    script = json.loads((proj / "script.json").read_text(encoding="utf-8"))
    lines = [ln for tk in script["takes"] for ln in tk["lines"]]
    photos = []
    pj = proj / "photos.json"
    if pj.exists():
        photos = json.loads(pj.read_text(encoding="utf-8")).get("photos", [])
    photos = [p for p in photos if p.get("kind", "photo") == "photo"]

    n = len(photos)
    xs = {p["id"]: (i - (n - 1) / 2) * 4600 for i, p in enumerate(photos)}
    # photo i enters at an evenly spread line (author remaps to word cues)
    enter = {}
    for i, p in enumerate(photos):
        li = min(len(lines) - 1, (i + 1) * len(lines) // (n + 1)) if lines else 0
        enter[p["id"]] = lines[li]["id"] if lines else 1

    body = []
    for i, p in enumerate(photos):
        x, lid = xs[p["id"]], enter[p["id"]]
        label = (p.get("what") or p["id"]).replace('"', "'")
        body.append(f'    film.add(Print("{p["id"]}", {x:.0f}, 0, 2400, rot={-1.5 + i:.1f}, '
                    f't_in=L({lid}) + 0.1, label="{label}", label_t=L({lid}) + 0.4))')
    for i in range(n - 1):
        a_id, b_id = photos[i]["id"], photos[i + 1]["id"]
        body.append(f'    film.add(StringLine(({xs[a_id]:.0f}, -300), ({xs[b_id]:.0f}, -300), '
                    f't_in=L({enter[b_id]}) - 0.2, dur=0.8, width=16, persist=True))')

    events = []
    for ln in lines:
        lid, spoken = ln["id"], ln.get("spoken", "")
        if ln.get("typed"):
            events.append(f'    film.add(BigText({ln["typed"]!r}, 0, -2500, 520, L({lid}) - 0.1, '
                          f't_out=E({lid}), type_on=0.6, rgb=(30, 26, 22), bar=(212, 164, 32), shadow=False))')
        m = NUM.search(spoken.replace(",", ""))
        if m and float(m.group()) >= 60:
            events.append(f'    film.add(Counter(0, 2300, 700, {m.group()}, L({lid}) + 0.3, '
                          f'dur=1.0, t_out=E({lid})))')
        for v in VERDICTS:
            if v in spoken:
                events.append(f'    film.add(Stamp({v!r}, 0, 200, size=640, rot=-9, t_in=E({lid}) - 0.45))')
                break

    cams = ['    cam(0, 0, 0, 0.16, 0)']
    for p in photos:
        lid = enter[p["id"]]
        cams.append(f'    cam(L({lid}) + 0.2, {xs[p["id"]]:.0f}, 0, 0.52, 0)')
    cams.append('    cam(doc.duration, 0, 0, 0.14, 0)')

    scene = f'''# Starter scene scaffolded by scaffold_scene.py — author from here.
# Style pack: {a.style} (see stylepacks.py). Regenerate into another name only.
from engine import BigText, Counter, Film, Print, Stamp, StringLine


def build_film(doc):
    L, E, W = doc.L, doc.E, doc.W
    film = Film(doc.duration, fps=30, look="wall")
    cam = film.cam
{chr(10).join(body)}
{chr(10).join(events)}
{chr(10).join(cams)}
    film.fade_in, film.fade_out = 0.9, 2.0
    return film
'''
    out.write_text(scene, encoding="utf-8")
    print(f"scaffold -> {out} (photos={n}, events={len(events)}, enter={enter})")


if __name__ == "__main__":
    main()

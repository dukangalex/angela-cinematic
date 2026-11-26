#!/usr/bin/env python3
"""One-command film pipeline: script.json in, draft.mp4 out.

Stages (each skipped when its outputs already exist, unless --force):
  fetch    fetch_commons.py get            photos + license ledger
  assets   make_map.py + prep_assets.py    maps, graded photos, textures
  takes    tts_takes.py                    production voice (needs DEPLOYMENT
                                           config: flags here or engine/
                                           DEPLOYMENT.json); or tts_say.py
                                           scratch voice with --scratch
  timing   split_takes.py + build_narration.py
  render   render.py                       the film itself
  finish   build_sfx.py + mix_soundtrack.py + burn_captions.py (opt-in)

The scene is the creative step and stays human/agent-authored: this script
stops with a clear message when scene.py is missing instead of inventing one.

  python3 make_film.py --project my-film --size 1280x720
  python3 make_film.py --project my-film --from render --finish
"""
import argparse, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).parent
STAGES = ["fetch", "assets", "takes", "timing", "render", "finish"]


def stage(name, cmd, proj):
    print(f"\n== {name}: {' '.join(cmd)}", flush=True)
    t0 = time.time()
    r = subprocess.run(cmd)
    if r.returncode != 0:
        sys.exit(f"stage {name} failed (exit {r.returncode}) — fix and re-run; "
                 f"completed stages are kept")
    print(f"== {name} done in {time.time() - t0:.0f}s", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--size", default="1280x720")
    ap.add_argument("--from", dest="frm", choices=STAGES, default=None)
    ap.add_argument("--to", dest="to", choices=STAGES, default="render")
    ap.add_argument("--force", action="store_true", help="redo stages even if outputs exist")
    ap.add_argument("--scratch", action="store_true", help="takes: use the local scratch voice (tts_say.py)")
    ap.add_argument("--finish", action="store_true", help="run the finish stage (sfx, mix, captions)")
    ap.add_argument("--voice", default=None)
    ap.add_argument("--rate", default=None)
    ap.add_argument("--proxy", default=None)
    a = ap.parse_args()

    proj = Path(a.project).resolve()
    py = sys.executable
    if not (proj / "script.json").exists():
        sys.exit(f"{proj}/script.json not found")

    todo = STAGES[STAGES.index(a.frm) if a.frm else 0: STAGES.index(a.to) + 1]
    if a.finish and "finish" not in todo:
        todo.append("finish")

    def have(p):
        return p.exists() and p.stat().st_size > 0

    for s in todo:
        if s == "fetch":
            if a.force or not have(proj / "photos.json"):
                stage(s, [py, str(HERE / "fetch_commons.py"), "get", "--project", str(proj)], proj)
        elif s == "assets":
            if a.force or not (proj / "assets" / "prep").exists():
                stage("map", [py, str(HERE / "make_map.py"), "--project", str(proj)], proj)
                stage(s, [py, str(HERE / "prep_assets.py"), "--project", str(proj)], proj)
        elif s == "takes":
            takes = proj / "audio" / "takes"
            if a.force or not (takes.exists() and any(takes.glob("*.wav"))):
                if a.scratch:
                    stage(s, [py, str(HERE / "tts_say.py"), "--project", str(proj)], proj)
                else:
                    cmd = [py, str(HERE / "tts_takes.py"), "--project", str(proj)]
                    for k in ("voice", "rate", "proxy"):
                        if getattr(a, k):
                            cmd += [f"--{k}", getattr(a, k)]
                    stage(s, cmd, proj)
        elif s == "timing":
            if a.force or not have(proj / "audio" / "timing.json"):
                stage("split", [py, str(HERE / "split_takes.py"), "--project", str(proj)], proj)
                stage(s, [py, str(HERE / "build_narration.py"), "--project", str(proj)], proj)
        elif s == "render":
            if not (proj / "scene.py").exists():
                sys.exit("scene.py missing — the scene is authored, not generated. "
                         "Write it (see examples/) and re-run with --from render.")
            out = proj / "out" / "draft.mp4"
            if a.force or not have(out):
                stage(s, [py, str(HERE / "render.py"), "--project", str(proj),
                          "--size", a.size, "--out", "out/draft.mp4",
                          "--audio", "audio/narration.m4a"], proj)
        elif s == "finish":
            stage("sfx", [py, str(HERE / "build_sfx.py"), "--project", str(proj)], proj)
            stage("mix", [py, str(HERE / "mix_soundtrack.py"), "--project", str(proj)], proj)
            stage("captions", [py, str(HERE / "burn_captions.py"), "--project", str(proj)], proj)
    print("\nmake_film: done")


if __name__ == "__main__":
    main()

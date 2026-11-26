#!/usr/bin/env python3
"""Record production takes for a project: one TTS call per script line,
lines joined with a fixed silence into one WAV per take.

Why per line: split_takes.py finds line boundaries in the silences, so the
joins must be clean, known silences — a whole-take synthesis buries them in
the voice's own pauses. Existing line files are kept (delete to re-record).

Backends:
  edge   edge-tts (Microsoft voices, e.g. zh-CN-YunyangNeural). Needs a
         tunnel-type proxy for its WebSocket in restricted networks —
         see docs/DEPLOYMENT.md. Voice, rate and proxy are deployment
         config (flags or DEPLOYMENT.json next to this script), never
         baked into a project.
  cmd    any TTS command: --cmd 'my-tts --voice X --out {out} {text}'
         with {text} and {out} substituted per line.

  python3 tts_takes.py --project my-film --voice zh-CN-YunyangNeural --rate +30%
  python3 tts_takes.py --project my-film --config /path/to/DEPLOYMENT.json
"""
import argparse, json, subprocess, sys, tempfile
from pathlib import Path

RATE = 24000


def run(cmd, **kw):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL, **kw)


def synth_edge(text, out_mp3, voice, rate, proxy, edge_bin):
    cmd = [edge_bin, "--voice", voice, "--text", text, "--write-media", str(out_mp3)]
    if rate:
        cmd[1:1] = ["--rate", rate]
    if proxy:
        cmd[1:1] = ["--proxy", proxy]
    run(cmd)


def synth_cmd(text, out_mp3, template):
    run(template.replace("{text}", text).replace("{out}", str(out_mp3)),
        shell=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--backend", choices=["edge", "cmd"], default=None)
    ap.add_argument("--voice", default=None)
    ap.add_argument("--rate", default=None)
    ap.add_argument("--proxy", default=None)
    ap.add_argument("--cmd", default=None, help="cmd backend template with {text} and {out}")
    ap.add_argument("--edge-bin", default="edge-tts")
    ap.add_argument("--gap", type=float, default=0.7, help="silence between lines, seconds")
    ap.add_argument("--config", default=None, help="DEPLOYMENT.json with voice/rate/proxy/backend/cmd")
    a = ap.parse_args()

    cfg = {}
    cfg_path = Path(a.config) if a.config else Path(__file__).with_name("DEPLOYMENT.json")
    if cfg_path.exists():
        cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    backend = a.backend or cfg.get("backend", "edge")
    voice = a.voice or cfg.get("voice")
    rate = a.rate or cfg.get("rate")
    proxy = a.proxy or cfg.get("proxy")
    template = a.cmd or cfg.get("cmd")
    if backend == "edge" and not voice:
        sys.exit("edge backend needs --voice (or voice in DEPLOYMENT.json)")
    if backend == "cmd" and not template:
        sys.exit("cmd backend needs --cmd template (or cmd in DEPLOYMENT.json)")

    proj = Path(a.project)
    script = json.loads((proj / "script.json").read_text(encoding="utf-8"))
    takes_dir = proj / "audio" / "takes"
    takes_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        sil = td / "sil.wav"
        run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i",
             f"anullsrc=r={RATE}:cl=mono", "-t", str(a.gap), str(sil), "-y"])
        for take in script["takes"]:
            name = take["take"]
            out = takes_dir / f"{name}.wav"
            if out.exists():
                print(f"{name}: exists, skipped")
                continue
            parts = []
            for ln in take["lines"]:
                mp3, wav = td / f"{name}_{ln['id']}.mp3", td / f"{name}_{ln['id']}.wav"
                if backend == "edge":
                    synth_edge(ln["spoken"], mp3, voice, rate, proxy, a.edge_bin)
                else:
                    synth_cmd(ln["spoken"], mp3, template)
                run(["ffmpeg", "-v", "error", "-i", str(mp3), "-ar", str(RATE),
                     "-ac", "1", str(wav), "-y"])
                parts.append(wav)
            lst = td / f"{name}.txt"
            with open(lst, "w") as f:
                for i, w in enumerate(parts):
                    f.write(f"file '{w}'\n")
                    if i < len(parts) - 1:
                        f.write(f"file '{sil}'\n")
            run(["ffmpeg", "-v", "error", "-f", "concat", "-safe", "0",
                 "-i", str(lst), "-c", "copy", str(out), "-y"])
            dur = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                                  "format=duration", "-of", "csv=p=0", str(out)],
                                 capture_output=True, text=True).stdout.strip()
            print(f"{name}: {len(parts)} lines, {dur}s")
    print("takes done ->", takes_dir)


if __name__ == "__main__":
    main()

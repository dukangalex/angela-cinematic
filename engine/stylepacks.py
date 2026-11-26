"""The 11 style presets as code: palette, font slots and pacing in one dict,
so choosing a style is an argument, not a document to re-read. The prose
versions live in styles/*.md and stay the reference for *why*; this module
is the *what* a scene actually consumes.

  from stylepacks import pack
  P = pack("chalkboard")
  doc.add(BigText("标题", ..., rgb=P["ink"], font=P["font_display"]))
"""
import sys

PACKS = {
    "wall":        dict(ink=(238, 231, 214), accent=(212, 164, 32), danger=(176, 30, 26),
                        font_display="cond", font_hand="hand", font_body="serif", cam_speed=1.0),
    "plotter":     dict(ink=(24, 26, 30), accent=(30, 90, 200), danger=(200, 40, 30),
                        font_display="cond", font_hand="cond", font_body="serif", cam_speed=0.9),
    "whiteboard":  dict(ink=(30, 34, 44), accent=(28, 96, 200), danger=(216, 44, 36),
                        font_display="hand", font_hand="hand", font_body="hand", cam_speed=1.1),
    "chalkboard":  dict(ink=(238, 242, 236), accent=(245, 213, 110), danger=(240, 120, 110),
                        font_display="hand", font_hand="hand", font_body="hand", cam_speed=1.0),
    "stickman":    dict(ink=(20, 20, 20), accent=(230, 60, 40), danger=(230, 60, 40),
                        font_display="hand", font_hand="hand", font_body="hand", cam_speed=1.25),
    "isometric":   dict(ink=(28, 32, 44), accent=(50, 120, 220), danger=(220, 70, 50),
                        font_display="cond", font_hand="cond", font_body="serif", cam_speed=0.9),
    "fake3d":      dict(ink=(26, 28, 36), accent=(240, 180, 60), danger=(220, 60, 50),
                        font_display="cond", font_hand="hand", font_body="serif", cam_speed=1.0),
    "infographic": dict(ink=(24, 28, 38), accent=(30, 130, 200), danger=(216, 48, 49),
                        font_display="cond", font_hand="cond", font_body="serif", cam_speed=1.1),
    "map-journey": dict(ink=(240, 234, 216), accent=(200, 60, 40), danger=(176, 30, 26),
                        font_display="cond", font_hand="hand", font_body="serif", cam_speed=0.85),
    "product":     dict(ink=(22, 24, 28), accent=(120, 90, 220), danger=(220, 60, 60),
                        font_display="cond", font_hand="cond", font_body="serif", cam_speed=1.0),
    "doodle":      dict(ink=(26, 24, 22), accent=(240, 110, 60), danger=(220, 50, 60),
                        font_display="hand", font_hand="hand", font_body="hand", cam_speed=1.2),
}


def names():
    return list(PACKS)


def pack(name):
    if name not in PACKS:
        raise KeyError(f"unknown style {name!r}; choose from {', '.join(PACKS)}")
    return dict(PACKS[name])


if __name__ == "__main__":
    if "--list" in sys.argv:
        for n, p in PACKS.items():
            print(f"{n:12s} accent={p['accent']} display={p['font_display']} cam_speed={p['cam_speed']}")
    else:
        print("usage: stylepacks.py --list")

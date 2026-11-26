"""Vertical and multi-aspect helpers.

The engine renders any --size; what vertical actually needs is framing
discipline: platform UI eats the top and bottom of a 9:16 frame, so key
elements must live in the safe band. World units are 4K pixels at zoom 1,
so a camera stop (cx, cy, zoom) over a W x H render shows a world rect of
(3840/zoom * W/3840) — SafeFrame draws the safe band for one such stop,
for draft renders while authoring. Leave it out of the final scene.

  film.add(SafeFrame(0, 0, 0.5, 1080, 1920))   # authoring aid
"""
import skia
from engine import Item, paint

SIZES = {"16:9": (1920, 1080), "9:16": (1080, 1920), "1:1": (1080, 1080),
         "4:5": (1080, 1350), "3:4": (1080, 1440)}


def safe_insets(w, h):
    """Fractions of the frame kept clear of platform UI, by aspect."""
    if h > w * 1.3:      # vertical: caption, buttons, progress bars
        return dict(top=0.13, bottom=0.20, left=0.06, right=0.06)
    if h > w:            # square-ish: lighter touch
        return dict(top=0.08, bottom=0.10, left=0.05, right=0.05)
    return dict(top=0.05, bottom=0.06, left=0.04, right=0.04)


def visible_world(zoom, w, h):
    """World-unit size of the viewport: the renderer scales by
    (render_width / 3840) * zoom, so width is always 3840/zoom and
    height follows the render aspect."""
    vw = 3840.0 / zoom
    return vw, vw * h / w


class SafeFrame(Item):
    z = 999

    def __init__(self, cx, cy, zoom, w, h):
        super().__init__(0, None, None, False)
        self.cx, self.cy, self.zoom, self.w, self.h = cx, cy, zoom, w, h

    def bounds(self, res):
        vw, vh = visible_world(self.zoom, self.w, self.h)
        return skia.Rect.MakeLTRB(self.cx - vw / 2, self.cy - vh / 2,
                                  self.cx + vw / 2, self.cy + vh / 2)

    def draw(self, c, res, t):
        vw, vh = visible_world(self.zoom, self.w, self.h)
        ins = safe_insets(self.w, self.h)
        x0, x1 = self.cx - vw / 2 + vw * ins["left"], self.cx + vw / 2 - vw * ins["right"]
        y0, y1 = self.cy - vh / 2 + vh * ins["top"], self.cy + vh / 2 - vh * ins["bottom"]
        p = paint((80, 220, 120), 0.9, stroke=14)
        c.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), p)
        c.drawLine(self.cx, self.cy - vh / 2, self.cx, self.cy + vh / 2,
                   paint((80, 220, 120), 0.35, stroke=8))
        c.drawLine(self.cx - vw / 2, self.cy, self.cx + vw / 2, self.cy,
                   paint((80, 220, 120), 0.35, stroke=8))

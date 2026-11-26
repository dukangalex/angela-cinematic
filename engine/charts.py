"""Data primitives for the infographic family: bar chart, line chart, donut.

Same element protocol as engine.py (Item subclass, draw(c, res, t)).
Data is plain [(label, value), ...]; everything animates in from t_in —
bars grow, the line draws itself, the donut sweeps. Values and labels are
drawn with the project's own fonts, so a chart looks like part of the film,
not a screenshot pasted in.

  BarChart(600, 500, 1500, 800, [("甲", 12), ("乙", 30)], t_in, rgb=ACCENT)
  LineChart(600, 500, 1500, 800, [3, 7, 6, 12, 20], t_in)
  Donut(960, 800, 330, [("直连", 62), ("代理", 38)], t_in)
"""
import skia
from engine import (Item, draw_text, paint, ramp, ease_out_cubic, clamp,
                    partial_path, CREAM, WHITE)

PALETTE = [(212, 164, 32), (176, 30, 26), (64, 145, 160), (96, 160, 84),
           (150, 110, 190), (210, 120, 60)]


class BarChart(Item):
    z = 60

    def __init__(self, x, y, w, h, data, t_in, dur=1.2, rgb=None, font="cond",
                 t_out=None, max_v=None):
        super().__init__(t_in, t_out, None, False)
        self.x, self.y, self.w, self.h, self.data, self.dur = x, y, w, h, data, dur
        self.rgb, self.font = rgb, font
        self.max_v = max_v or max(v for _, v in data) or 1

    def bounds(self, res):
        return skia.Rect.MakeXYWH(self.x - 80, self.y - 80, self.w + 160, self.h + 260)

    def draw(self, c, res, t):
        a = ramp(t, self.t_in, 0.3) * self.fade(t)
        if a <= 0:
            return
        n = len(self.data)
        slot = self.w / n
        bw = slot * 0.58
        base = self.y + self.h
        c.drawLine(self.x, base, self.x + self.w, base, paint(CREAM, a * 0.85, stroke=5))
        for i, (label, v) in enumerate(self.data):
            u = ease_out_cubic(ramp(t, self.t_in + i * 0.12, self.dur))
            bh = self.h * (v / self.max_v) * u
            bx = self.x + i * slot + (slot - bw) / 2
            col = self.rgb or PALETTE[i % len(PALETTE)]
            c.drawRect(skia.Rect.MakeXYWH(bx, base - bh, bw, bh), paint(col, a))
            if u > 0.85:
                draw_text(c, res, f"{v:g}", bx + bw / 2, base - bh - 26,
                          84, self.font, WHITE, a * u, 0.02, "center")
            draw_text(c, res, str(label), bx + bw / 2, base + 108,
                      76, self.font, CREAM, a, 0.02, "center")


class LineChart(Item):
    z = 60

    def __init__(self, x, y, w, h, values, t_in, dur=1.4, rgb=(212, 164, 32),
                 font="cond", t_out=None, labels=None, max_v=None):
        super().__init__(t_in, t_out, None, False)
        self.x, self.y, self.w, self.h = x, y, w, h
        self.values, self.dur, self.rgb, self.font = values, dur, rgb, font
        self.labels = labels
        self.max_v = max_v or max(values) or 1

    def bounds(self, res):
        return skia.Rect.MakeXYWH(self.x - 80, self.y - 80, self.w + 160, self.h + 260)

    def _points(self):
        n = len(self.values)
        return [(self.x + self.w * (i / (n - 1) if n > 1 else 0),
                 self.y + self.h * (1 - v / self.max_v))
                for i, v in enumerate(self.values)]

    def draw(self, c, res, t):
        a = ramp(t, self.t_in, 0.3) * self.fade(t)
        if a <= 0:
            return
        base = self.y + self.h
        c.drawLine(self.x, base, self.x + self.w, base, paint(CREAM, a * 0.85, stroke=5))
        pts = self._points()
        path = skia.Path()
        path.moveTo(*pts[0])
        for p in pts[1:]:
            path.lineTo(*p)
        u = ease_out_cubic(ramp(t, self.t_in, self.dur))
        sub = partial_path(path, u)
        if sub:
            c.drawPath(sub, paint(self.rgb, a, stroke=10))
        shown = max(1, int(round(u * (len(pts) - 1))))
        for i, (px, py) in enumerate(pts[:shown + 1]):
            c.drawCircle(px, py, 15, paint(WHITE, a))
            if self.labels:
                draw_text(c, res, str(self.labels[i]), px, base + 108,
                          72, self.font, CREAM, a, 0.02, "center")


class Donut(Item):
    z = 60

    def __init__(self, x, y, r, data, t_in, dur=1.4, font="cond", t_out=None,
                 center_label=None):
        super().__init__(t_in, t_out, None, False)
        self.x, self.y, self.r, self.data, self.dur = x, y, r, data, dur
        self.font, self.center_label = font, center_label
        self.total = sum(v for _, v in data) or 1

    def bounds(self, res):
        r = self.r + 320
        return skia.Rect.MakeLTRB(self.x - r, self.y - r, self.x + r, self.y + r)

    def draw(self, c, res, t):
        a = ramp(t, self.t_in, 0.3) * self.fade(t)
        if a <= 0:
            return
        u = ease_out_cubic(ramp(t, self.t_in, self.dur))
        rect = skia.Rect.MakeXYWH(self.x - self.r, self.y - self.r,
                                  self.r * 2, self.r * 2)
        start = -90.0
        thick = self.r * 0.34
        for i, (label, v) in enumerate(self.data):
            sweep_full = 360.0 * v / self.total
            sweep = sweep_full * clamp(u * len(self.data) - i, 0.0, 1.0)
            if sweep > 0.5:
                c.drawArc(rect, start, sweep - 2, False,
                          paint(PALETTE[i % len(PALETTE)], a, stroke=thick))
            start += sweep_full
        if self.center_label and u > 0.7:
            draw_text(c, res, self.center_label, self.x, self.y + 40,
                      96, self.font, WHITE, a * (u - 0.7) / 0.3, 0.02, "center")
        ly = self.y - (len(self.data) - 1) * 52
        for i, (label, v) in enumerate(self.data):
            col = PALETTE[i % len(PALETTE)]
            lx = self.x + self.r + 90
            c.drawRect(skia.Rect.MakeXYWH(lx, ly + i * 104 - 34, 52, 52), paint(col, a))
            draw_text(c, res, f"{label} {v:g}", lx + 76, ly + i * 104 + 26,
                      76, self.font, CREAM, a, 0.02, "left")

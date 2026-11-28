"""核查语法组件：画内时钟、同钟标尺、已知／未知分栏。

[angela-cinematic] 自写组件，配合核实模板（templates/verify）使用。
核实的说服力一半在画面本身：时间要画在画面里、两路证据要锁在同一把
时钟上对照、查清的和没查清的分开摆，推断必须标明是推断。这三件都是
构图层组件，不依赖任何底纹风格，wall 之外也能用。

  FrameClock(x, y, t_in, start=37.0, label="监控原片")     证据自带的时间读数
  SyncRuler(x, y, w, t_in, dur=6, span=90, pins=[...])     两路证据共用的标尺
  KnownUnknown(x, y, w, known=[...], unknown=[...], t_in)  已知／未知分栏板

约定：pins 里的 frac 是证据时间轴上的位置（0..1），两枚针落在同一 frac
就是「同一时刻」；unknown 条目可写 (文字, True) 表示这一条是推断，
画面上会挂红色描边的「推断」签，虚线边框与实线边框的对位本身就是口径。
"""
import skia
from engine import (Item, draw_text, text_width, paint, ramp, ease_out_cubic,
                    clamp, CREAM, WHITE, INK)

RED = (196, 44, 34)
GOLD = (212, 164, 32)
GREEN = (110, 190, 110)
DIGITS = (140, 255, 150)


def dash_line(c, x0, y0, x1, y1, p, dash=30.0, gap=20.0):
    """Straight dashed line (manual segments: no PathEffect dependency)."""
    dx, dy = x1 - x0, y1 - y0
    total = (dx * dx + dy * dy) ** 0.5
    if total <= 0:
        return
    ux, uy = dx / total, dy / total
    s = 0.0
    while s < total:
        e = min(s + dash, total)
        c.drawLine(x0 + ux * s, y0 + uy * s, x0 + ux * e, y0 + uy * e, p)
        s = e + gap


def _fmt_clock(v):
    v = max(0.0, v)
    if v >= 3600:
        h = int(v // 3600); m = int(v % 3600 // 60); s = v % 60
        return f"{h}:{m:02d}:{s:04.1f}"
    m = int(v // 60); s = v % 60
    return f"{m:02d}:{s:04.1f}"


class FrameClock(Item):
    """证据画面自带的时间读数：深色牌面＋红点＋等宽数字，随片内时间走。

    start 是证据自己的起始秒，speed 是证据时间对影片时间的倍率（慢放
    0.5、倍速 2）；freeze 给定后读数走到该值停住并亮出「冻帧」签——
    核实片里把关键一秒冻在画面上，比旁白念时间戳有力得多。
    """
    z = 65

    def __init__(self, x, y, t_in, start=0.0, speed=1.0, label=None, size=270,
                 freeze=None, t_out=None, rgb=DIGITS):
        super().__init__(t_in, t_out, None, False)
        self.x, self.y, self.start, self.speed = x, y, start, speed
        self.label, self.size, self.freeze, self.rgb = label, size, freeze, rgb

    def _value(self, t):
        v = self.start + (t - self.t_in) * self.speed
        return min(v, self.freeze) if self.freeze is not None else v

    def bounds(self, res):
        w = text_width(res, "00:00.0", self.size, "mono", 0.02) + self.size * 1.5
        return skia.Rect.MakeXYWH(self.x - 60, self.y - self.size * 1.2, w + 120, self.size * 2.4)

    def draw(self, c, res, t):
        a = ramp(t, self.t_in, 0.3) * self.fade(t)
        if a <= 0:
            return
        txt = _fmt_clock(self._value(t))
        tw = text_width(res, txt, self.size, "mono", 0.02)
        pad = self.size * 0.42
        w, h = tw + pad * 2 + self.size * 0.75, self.size * 1.52
        rect = skia.Rect.MakeXYWH(self.x, self.y, w, h)
        c.drawRoundRect(rect, 36, 36, paint((16, 18, 16), a * 0.88))
        c.drawRoundRect(rect, 36, 36, paint(CREAM, a * 0.5, stroke=5))
        if self.label:
            draw_text(c, res, self.label, self.x + 6, self.y - self.size * 0.28,
                      self.size * 0.42, "body", CREAM, a, 0.02)
        frozen = self.freeze is not None and self._value(t) >= self.freeze - 1e-9
        if not frozen and int(t * 2) % 2 == 0:
            c.drawCircle(self.x + pad * 0.72, self.y + h / 2, self.size * 0.13, paint(RED, a))
        draw_text(c, res, txt, self.x + pad + self.size * 0.55, self.y + h / 2 + self.size * 0.36,
                  self.size, "mono", self.rgb, a, 0.02)
        if frozen:
            tag = "冻帧"
            tw2 = text_width(res, tag, self.size * 0.4, "body", 0.04)
            tx, ty = self.x + w + 30, self.y + h * 0.14
            c.drawRoundRect(skia.Rect.MakeXYWH(tx, ty, tw2 + 56, self.size * 0.62), 14, 14,
                            paint(RED, a, stroke=6))
            draw_text(c, res, tag, tx + 28, ty + self.size * 0.46, self.size * 0.4,
                      "body", (255, 150, 140), a, 0.04)


class SyncRuler(Item):
    """同钟标尺：两路证据共用的一把时间尺。

    一条横尺代表 span 秒的证据时间，pins 是各路证据在尺上的对齐点：
    两枚针 frac 相同即同一时刻，针上拉一条虚线穿过上下两份证据，
    观众一眼能看出「对没对齐」。playhead 随影片时间扫过全尺，
    走到针位时旁白正好说到那一秒——尺、画面、旁白三者同钟。
    pins: [(frac, 标签, 颜色), ...]，同 frac 可多枚（标签上下错开）。
    """
    z = 62

    def __init__(self, x, y, w, t_in, dur=6.0, span=90.0, pins=(), line_h=1500,
                 caption=None, t_out=None):
        super().__init__(t_in, t_out, None, False)
        self.x, self.y, self.w, self.dur, self.span = x, y, w, dur, span
        self.pins, self.line_h, self.caption = pins, line_h, caption

    def bounds(self, res):
        return skia.Rect.MakeXYWH(self.x - 80, self.y - self.line_h - 320,
                                  self.w + 160, self.line_h + 700)

    def draw(self, c, res, t):
        a = ramp(t, self.t_in, 0.4) * self.fade(t)
        if a <= 0:
            return
        x, y, w = self.x, self.y, self.w
        u = clamp((t - self.t_in) / self.dur) if self.dur > 0 else 1.0
        if self.caption:
            draw_text(c, res, self.caption, x + w / 2, y - self.line_h - 130,
                      120, "body", CREAM, a, 0.03, "center")
        c.drawLine(x, y, x + w, y, paint(CREAM, a * 0.9, stroke=7))
        steps = 10
        for i in range(steps + 1):
            tx = x + w * i / steps
            c.drawLine(tx, y - 26, tx, y + 26, paint(CREAM, a * 0.7, stroke=5))
            if i % 2 == 0:
                draw_text(c, res, f"{self.span * i / steps:g}", tx, y + 128,
                          76, "mono", CREAM, a * 0.75, 0.0, "center")
        rows = {}
        for frac, label, rgb in self.pins:
            px = x + w * clamp(frac)
            dash_line(c, px, y - 10, px, y - self.line_h, paint(rgb, a * 0.85, stroke=6))
            c.drawCircle(px, y, 26, paint(rgb, a))
            row = rows.get(frac, 0); rows[frac] = row + 1
            draw_text(c, res, label, px, y + 240 + row * 120, 92, "body", rgb, a, 0.02, "center")
        hx = x + w * ease_out_cubic(u)
        c.drawLine(hx, y - 90, hx, y + 90, paint(GOLD, a, stroke=10))
        path = skia.Path()
        path.moveTo(hx - 34, y - 150); path.lineTo(hx + 34, y - 150); path.lineTo(hx, y - 84)
        path.close()
        c.drawPath(path, paint(GOLD, a))


class KnownUnknown(Item):
    """已知／未知分栏板：查清的靠左实线摆，没查清的靠右虚线摆。

    known 是已核实的条目（对勾），unknown 是还没核实的（问号）；
    unknown 条目写成 (文字, True) 表示推断——挂红色「推断」签，
    且整栏用虚线边框，与已知栏的实线形成口径对位。条目逐条落下，
    旁白说到哪条、哪条亮出来。条目文字保持一句话，超长不换行。
    """
    z = 62

    def __init__(self, x, y, w, known, unknown, t_in, row_h=200, t_out=None):
        super().__init__(t_in, t_out, None, False)
        self.x, self.y, self.w = x, y, w
        self.known, self.unknown, self.row_h = known, unknown, row_h

    def _panel_h(self):
        return 250 + max(len(self.known), len(self.unknown)) * self.row_h + 50

    def bounds(self, res):
        return skia.Rect.MakeXYWH(self.x - 60, self.y - 60, self.w + 120, self._panel_h() + 120)

    def _panel(self, c, res, t, px, pw, title, items, known_side):
        a_head = ramp(t, self.t_in, 0.35) * self.fade(t)
        if a_head <= 0:
            return
        ph = self._panel_h()
        rect = skia.Rect.MakeXYWH(px, self.y, pw, ph)
        c.drawRoundRect(rect, 26, 26, paint((18, 17, 13), a_head * 0.72))
        if known_side:
            c.drawRoundRect(rect, 26, 26, paint(CREAM, a_head * 0.85, stroke=6))
        else:
            dash_line(c, px, self.y, px + pw, self.y, paint(GOLD, a_head * 0.9, stroke=6))
            dash_line(c, px, self.y + ph, px + pw, self.y + ph, paint(GOLD, a_head * 0.9, stroke=6))
            dash_line(c, px, self.y, px, self.y + ph, paint(GOLD, a_head * 0.9, stroke=6))
            dash_line(c, px + pw, self.y, px + pw, self.y + ph, paint(GOLD, a_head * 0.9, stroke=6))
        draw_text(c, res, title, px + 56, self.y + 168, 138, "body",
                  CREAM if known_side else GOLD, a_head, 0.06)
        c.drawLine(px + 40, self.y + 218, px + pw - 40, self.y + 218,
                   paint(CREAM if known_side else GOLD, a_head * 0.45, stroke=4))
        for i, item in enumerate(items):
            text, inferred = item if isinstance(item, tuple) else (item, False)
            ai = ramp(t, self.t_in + 0.45 + i * 0.3, 0.3) * self.fade(t)
            if ai <= 0:
                continue
            ry = self.y + 250 + i * self.row_h + 118
            if known_side:
                # check drawn as strokes: the ✓ glyph is missing from the
                # CJK faces and would land as a tofu box
                p = paint(GREEN, ai, stroke=11)
                c.drawLine(px + 62, ry - 34, px + 96, ry - 4, p)
                c.drawLine(px + 96, ry - 4, px + 158, ry - 88, p)
            else:
                draw_text(c, res, "?", px + 62, ry, 108, "body", GOLD, ai, 0.0)
            draw_text(c, res, text, px + 190, ry, 104, "body", CREAM, ai, 0.01)
            if inferred:
                tag = "推断"
                tw = text_width(res, tag, 78, "body", 0.04)
                tx = px + pw - tw - 110
                c.drawRoundRect(skia.Rect.MakeXYWH(tx - 24, ry - 84, tw + 48, 108), 12, 12,
                                paint(RED, ai, stroke=5))
                draw_text(c, res, tag, tx, ry - 8, 78, "body", (255, 150, 140), ai, 0.04)

    def draw(self, c, res, t):
        gap = 130
        pw = (self.w - gap) / 2
        self._panel(c, res, t, self.x, pw, "已知", self.known, True)
        self._panel(c, res, t, self.x + pw + gap, pw, "未知", self.unknown, False)

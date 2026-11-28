"""教程图解三件：步骤图、线条剖面、分层爆炸。

[angela-cinematic] 自写组件，配合教程模板（templates/tutorial）使用。
教程片最缺的不是图卡，是「把结构画出来」：操作要有编号步骤图、
内部构造要有剖面、组合关系要有分层拆解。三件全是 2D 线面绘制，
不吃素材，任何题材都能现画。文字保持短句，本模块不做自动换行，
多行说明在字符串里用换行符断行。

  StepFlow(x, y, [(标题, 说明), ...], t_in)                    编号步骤链
  Cutaway(x, y, w, h, [(标签, fx, fy, fw, fh, 侧), ...], t_in)  线条剖面
  ExplodedLayers(x, y, [(标签, 颜色), ...], t_in)               分层拆开
"""
import skia
from engine import (Item, draw_text, text_width, paint, ramp, ease_out_cubic,
                    ease_out_back, clamp, CREAM, WHITE, INK)
from evidence import dash_line

GOLD = (212, 164, 32)
PAPER = (238, 231, 214)
INKSOFT = (84, 74, 60)
LAYER_COLORS = [(212, 164, 32), (64, 145, 160), (150, 110, 190),
                (96, 160, 84), (210, 120, 60), (176, 30, 26)]


class StepFlow(Item):
    """编号步骤链：纸面方框横向排开，金色序号徽章压在框角，箭头逐个接上。

    steps 是 (标题, 说明) 列表，说明可带换行符分行。第 i 步在
    t_in + i*stagger 落下，箭头在下一步落下前画完——旁白讲到哪步，
    画面就走到哪步，最后一步的框边加金色描边表示「当前」。
    """
    z = 60

    def __init__(self, x, y, steps, t_in, box_w=1420, box_h=660, gap=330,
                 stagger=0.9, t_out=None):
        super().__init__(t_in, t_out, None, False)
        self.x, self.y, self.steps = x, y, steps
        self.box_w, self.box_h, self.gap, self.stagger = box_w, box_h, gap, stagger

    def _total_w(self):
        n = len(self.steps)
        return n * self.box_w + (n - 1) * self.gap

    def bounds(self, res):
        return skia.Rect.MakeXYWH(self.x - 140, self.y - 160,
                                  self._total_w() + 280, self.box_h + 320)

    def draw(self, c, res, t):
        n = len(self.steps)
        for i, (title, note) in enumerate(self.steps):
            ti = self.t_in + i * self.stagger
            a = ramp(t, ti, 0.3) * self.fade(t)
            if a <= 0:
                continue
            bx = self.x + i * (self.box_w + self.gap)
            by = self.y + (1 - ease_out_cubic(ramp(t, ti, 0.45))) * -46
            rect = skia.Rect.MakeXYWH(bx, by, self.box_w, self.box_h)
            c.drawRoundRect(rect, 22, 22, paint(PAPER, a * 0.96))
            if i == n - 1 or t < self.t_in + (i + 1) * self.stagger:
                c.drawRoundRect(rect, 22, 22, paint(GOLD, a, stroke=10))
            draw_text(c, res, title, bx + 70, by + 240, 168, "body", INK, a, 0.02)
            for j, line in enumerate(note.split("\n")):
                draw_text(c, res, line, bx + 70, by + 400 + j * 128, 102, "body",
                          INKSOFT, a, 0.01)
            c.drawCircle(bx + 6, by + 6, 104, paint(GOLD, a))
            c.drawCircle(bx + 6, by + 6, 104, paint(INK, a * 0.25, stroke=4))
            draw_text(c, res, str(i + 1), bx + 6, by + 44, 128, "cond", INK, a, 0.0, "center")
            if i < n - 1:
                ax0, ax1 = bx + self.box_w + 36, bx + self.box_w + self.gap - 36
                ay = self.y + self.box_h / 2
                u = clamp((t - ti - self.stagger * 0.45) / (self.stagger * 0.5))
                if u > 0:
                    ex = ax0 + (ax1 - ax0) * ease_out_cubic(u)
                    aa = a * self.fade(t)
                    c.drawLine(ax0, ay, ex, ay, paint(GOLD, aa, stroke=13))
                    if u > 0.85:
                        path = skia.Path()
                        path.moveTo(ax1 + 26, ay); path.lineTo(ax1 - 52, ay - 40)
                        path.lineTo(ax1 - 52, ay + 40); path.close()
                        c.drawPath(path, paint(GOLD, aa))


class Cutaway(Item):
    """线条剖面：外壳轮廓＋剖切标记，内部件逐个亮出，引线拉到两侧标注。

    parts 是 (标签, fx, fy, fw, fh, 侧)：fx/fy 是部件中心在壳内的相对
    位置（0..1），fw/fh 是相对宽高，侧为 "L" 或 "R" 决定标注拉向哪边。
    壳顶的斜线带是剖切面标记，竖直虚线是剖面线，标签旁标 A—A。
    适合画「打开来看里面」：设备、文件结构、管线走向都可套。
    """
    z = 60

    def __init__(self, x, y, w, h, parts, t_in, title=None, rgb=CREAM,
                 accent=GOLD, stagger=0.35, t_out=None):
        super().__init__(t_in, t_out, None, False)
        self.x, self.y, self.w, self.h, self.parts = x, y, w, h, parts
        self.title, self.rgb, self.accent, self.stagger = title, rgb, accent, stagger

    def bounds(self, res):
        return skia.Rect.MakeXYWH(self.x - 900, self.y - 320, self.w + 1800, self.h + 520)

    def draw(self, c, res, t):
        a = ramp(t, self.t_in, 0.4) * self.fade(t)
        if a <= 0:
            return
        x, y, w, h = self.x, self.y, self.w, self.h
        if self.title:
            draw_text(c, res, self.title, x, y - 120, 132, "body", self.rgb, a, 0.03)
        rect = skia.Rect.MakeXYWH(x, y, w, h)
        c.drawRoundRect(rect, 30, 30, paint(self.rgb, a * 0.10))
        c.drawRoundRect(rect, 30, 30, paint(self.rgb, a * 0.9, stroke=9))
        band = 86
        c.save(); c.clipRRect(skia.RRect.MakeRectXY(rect, 30, 30), skia.ClipOp.kIntersect, True)
        hx = x - band
        while hx < x + w + band:
            c.drawLine(hx, y + band, hx + band, y, paint(self.accent, a * 0.8, stroke=10))
            hx += 64
        c.restore()
        sx = x + w * 0.34
        dash_line(c, sx, y - 66, sx, y + h + 66, paint(self.accent, a * 0.75, stroke=6))
        draw_text(c, res, "A—A", sx + 30, y + h + 150, 84, "mono", self.accent, a, 0.0)
        for i, (label, fx, fy, fw, fh, side) in enumerate(self.parts):
            ai = ramp(t, self.t_in + 0.5 + i * self.stagger, 0.3) * self.fade(t)
            if ai <= 0:
                continue
            pw, ph = w * fw, h * fh
            px, py = x + w * fx - pw / 2, y + h * fy - ph / 2
            prect = skia.Rect.MakeXYWH(px, py, pw, ph)
            c.drawRoundRect(prect, 16, 16, paint(self.accent, ai * 0.20))
            c.drawRoundRect(prect, 16, 16, paint(self.rgb, ai * 0.95, stroke=6))
            cy = py + ph / 2
            if side == "L":
                lx, anchor, tx = x - 90, px, x - 150
                c.drawLine(px, cy, lx, cy, paint(self.rgb, ai * 0.8, stroke=5))
                c.drawCircle(px, cy, 13, paint(self.accent, ai))
                draw_text(c, res, label, tx, cy + 40, 116, "body", self.rgb, ai, 0.01, "right")
            else:
                lx, anchor, tx = x + w + 90, px + pw, x + w + 150
                c.drawLine(px + pw, cy, lx, cy, paint(self.rgb, ai * 0.8, stroke=5))
                c.drawCircle(px + pw, cy, 13, paint(self.accent, ai))
                draw_text(c, res, label, tx, cy + 40, 116, "body", self.rgb, ai, 0.01, "left")


class ExplodedLayers(Item):
    """分层爆炸：叠在一起的层板沿竖直虚线导轨逐层拉开。

    layers 是 (标签, 颜色) 列表（颜色可省，用默认色序）。第 i 层在
    t_in + i*stagger 开始分离，间距由 0 长到 gap；两侧虚线导轨表示
    「拆开看仍对得齐」，标签在右侧以引线对到本层。适合画构成关系：
    一个订阅、一份配置、一条流水线由哪几层叠出来。
    """
    z = 60

    def __init__(self, x, y, layers, t_in, w=2050, layer_h=250, gap=265,
                 stagger=0.42, depth=95, t_out=None):
        super().__init__(t_in, t_out, None, False)
        self.x, self.y, self.layers = x, y, layers
        self.w, self.layer_h, self.gap = w, layer_h, gap
        self.stagger, self.depth = stagger, depth

    def _total_h(self):
        n = len(self.layers)
        return n * self.layer_h + (n - 1) * self.gap

    def bounds(self, res):
        return skia.Rect.MakeXYWH(self.x - 200, self.y - 200,
                                  self.w + 1500, self._total_h() + 400)

    def draw(self, c, res, t):
        a0 = ramp(t, self.t_in, 0.3) * self.fade(t)
        if a0 <= 0:
            return
        x, y = self.x, self.y
        th = self._total_h()
        for gx in (x - 78, x + self.w + 78):
            dash_line(c, gx, y - 40, gx, y + th + 40, paint(CREAM, a0 * 0.4, stroke=5))
        for i, item in enumerate(self.layers):
            label, rgb = item if isinstance(item, tuple) else (item, LAYER_COLORS[i % len(LAYER_COLORS)])
            ti = self.t_in + i * self.stagger
            ai = ramp(t, ti, 0.3) * self.fade(t)
            if ai <= 0:
                continue
            u = ease_out_cubic(ramp(t, ti, 0.85))
            ly = y + i * (self.layer_h + self.gap) * u + i * 14 * (1 - u)
            d = self.depth
            top = skia.Path()
            top.moveTo(x, ly); top.lineTo(x + d * 0.62, ly - d); top.lineTo(x + self.w + d * 0.62, ly - d)
            top.lineTo(x + self.w, ly); top.close()
            c.drawPath(top, paint(rgb, ai * 0.55))
            side = skia.Path()
            side.moveTo(x + self.w, ly); side.lineTo(x + self.w + d * 0.62, ly - d)
            side.lineTo(x + self.w + d * 0.62, ly - d + self.layer_h); side.lineTo(x + self.w, ly + self.layer_h)
            side.close()
            c.drawPath(side, paint(rgb, ai * 0.75))
            c.drawRect(skia.Rect.MakeXYWH(x, ly, self.w, self.layer_h), paint(rgb, ai * 0.92))
            cy = ly + self.layer_h / 2
            tx = x + self.w + d * 0.62 + 210
            c.drawLine(x + self.w + d * 0.62, cy, tx - 60, cy, paint(CREAM, ai * 0.8, stroke=5))
            draw_text(c, res, label, tx, cy + 42, 122, "body", CREAM, ai, 0.02)
            draw_text(c, res, str(i + 1), x + 66, cy + 52, 140, "cond",
                      (20, 18, 14), ai * 0.55, 0.0)

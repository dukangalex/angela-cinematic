# 核实类模板场景：原说法大字 → 证据照片 → 数据对照 → 结论印章。
# 改这里：VERDICT 四档选一（属实／基本属实／夸大／不实），与旁白结论一致。
# 核查语法（evidence.py）：证据带画内时钟、两路证据用同钟标尺对齐、
# 已知与未知分栏摆，推断条目挂「推断」签——用法见本模板 README。
from engine import BigText, Counter, Film, Print, Stamp, StringLine
from charts import BarChart
from evidence import FrameClock, KnownUnknown, SyncRuler

VERDICT = "夸大"


def build_film(doc):
    L, E, W = doc.L, doc.E, doc.W
    film = Film(doc.duration, fps=30, look="wall")
    cam = film.cam
    # 原说法
    film.add(BigText("原说法", -2600, -2400, 560, L(1) + 0.1, rgb=(238, 231, 214)))
    film.add(Print("P01", -2600, 0, 2400, rot=-1.2, t_in=L(1) + 0.3, label="原帖截图", label_t=L(1) + 0.6))
    # 核实证据
    film.add(Print("P02", 2600, 0, 2400, rot=1.4, t_in=L(3) + 0.2, label="一手来源", label_t=L(3) + 0.5))
    film.add(StringLine((-2600, -300), (2600, -300), t_in=L(3) + 0.1, dur=0.8, width=16, persist=True))
    # 画内时钟：压在证据图角上，读数是证据自己的时间（起始秒按实测填）
    film.add(FrameClock(1500, 620, L(3) + 0.4, start=0.0, label="一手来源原片时间"))
    # 同钟标尺：两枚针对同一 frac = 同一时刻对齐（标签与秒数换成实测值）
    film.add(SyncRuler(-3400, 1280, 6800, L(3) + 0.3, dur=max(2.0, E(3) - L(3)), span=90,
                       pins=[(0.42, "原帖 37.4 秒", (196, 90, 80)),
                             (0.42, "一手来源 37.4 秒", (212, 164, 32))],
                       line_h=1350, caption="同一时钟，全长 90 秒"))
    # 数据对照（示例数据，换成核实到的真实数字）
    film.add(BarChart(-2300, 1500, 4600, 2200, [("声称", 300), ("实际", 90)], L(4) + 0.2, t_out=E(4)))
    # 已知／未知分栏：查清的进左栏，未查清的进右栏，推断条目传 (文字, True)
    film.add(KnownUnknown(-2600, 1750, 5200,
                          known=["来源是官方账号", "数字出自原帖截图"],
                          unknown=[("转发量是否注水", True), "原始文件未公开"],
                          t_in=L(5) + 0.2))
    # 结论印章
    film.add(Stamp(VERDICT, 2600, 300, size=680, rot=-9, t_in=E(5) - 0.5))
    cam(0, -2600, -600, 0.34, 0)
    cam(L(3), 0, 0, 0.30, 0)
    cam(L(4), 0, 2400, 0.42, 0)
    cam(L(5), 0, 1700, 0.29, 0)
    cam(doc.duration, 0, 0, 0.15, 0)
    film.fade_in, film.fade_out = 0.9, 2.0
    return film

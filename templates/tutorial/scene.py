# 教程类模板场景：问题大字 → 步骤卡逐张落下 → 验证计数。
# 步骤的 typed 文字来自 script.json 的 typed 字段，改稿时同步。
# 图解三件（diagrams.py）在下半区：剖面（第 4 句中段）、分层（第 5 句中段）、
# 步骤链收尾复述（第 6 句）。用不上哪件删哪件，用法见本模板 README。
from engine import BigText, Counter, Film, Print, Stamp
from diagrams import Cutaway, ExplodedLayers, StepFlow


def build_film(doc):
    L, E, W = doc.L, doc.E, doc.W
    film = Film(doc.duration, fps=30, look="wall")
    cam = film.cam
    film.add(BigText("要解决的问题", 0, -2400, 560, L(1) + 0.1, rgb=(238, 231, 214)))
    film.add(Print("P01", 0, 0, 2600, rot=-1.0, t_in=L(2) + 0.2, label="准备清单", label_t=L(2) + 0.5))
    for i, lid in enumerate((3, 4, 5)):
        x = (i - 1) * 4200
        film.add(BigText(f"第{i + 1}步", x, -1500, 620, L(lid) + 0.1, font="hand", grunge=False,
                         rgb=(30, 26, 22), bar=(212, 164, 32), bar_h=0.92, shadow=False, t_out=E(lid)))
        film.add(Print(f"P{i + 2:02d}", x, 600, 2200, rot=-1.5 + i, t_in=L(lid) + 0.3,
                       label=f"步骤{i + 1}截图", label_t=L(lid) + 0.6))
    # 线条剖面：打开看内部（部件与标注换成你的对象）
    film.add(Cutaway(-1750, 2500, 3500, 1400,
                     [("电池", 0.28, 0.55, 0.30, 0.55, "L"),
                      ("主板", 0.62, 0.40, 0.34, 0.40, "R"),
                      ("接口", 0.63, 0.76, 0.30, 0.30, "R")],
                     L(4) + 1.0, title="剖面示例：打开看内部"))
    # 分层爆炸：一份东西由哪几层叠出来（层名换成你的构成）
    film.add(ExplodedLayers(-1025, 4600,
                            [("界面层", (212, 164, 32)), ("规则层", (64, 145, 160)),
                             ("数据层", (150, 110, 190))],
                            L(5) + 1.0))
    # 步骤链：收尾把三步连成一条链复述
    film.add(StepFlow(-2460, 6600,
                      [("第一步", "先准备好"), ("第二步", "照图操作"), ("第三步", "验一遍结果")],
                      L(6) + 0.2, stagger=0.8))
    film.add(Stamp("跑通", 0, 400, size=640, rot=-9, t_in=E(6) - 0.5))
    cam(0, 0, -600, 0.32, 0)
    for i, lid in enumerate((3, 4, 5)):
        cam(L(lid), (i - 1) * 4200, 0, 0.5, 0)
    cam(L(4) + 1.0, 0, 3200, 0.40, 0)
    cam(L(5) + 1.0, 300, 5200, 0.40, 0)
    cam(L(6), 0, 5600, 0.22, 0)
    cam(doc.duration, 0, 2400, 0.11, 0)
    film.fade_in, film.fade_out = 0.9, 2.0
    return film

# 教程类模板场景：问题大字 → 步骤卡逐张落下 → 验证计数。
# 步骤的 typed 文字来自 script.json 的 typed 字段，改稿时同步。
from engine import BigText, Counter, Film, Print, Stamp


def build_film(doc):
    L, E, W = doc.L, doc.E, doc.W
    film = Film(doc.duration, fps=30, look="wall")
    cam = film.cam
    film.add(BigText("要解决的问题", 0, -2400, 560, L(1) + 0.1, rgb=(238, 231, 214)))
    film.add(Print("P01", 0, 0, 2600, rot=-1.0, t_in=L(2) + 0.2, label="准备清单", label_t=L(2) + 0.5))
    for i, lid in enumerate((3, 4, 5)):
        x = (i - 1) * 4200
        film.add(BigText(f"第{i + 1}步", x, -1500, 620, L(lid) + 0.1,
                         rgb=(30, 26, 22), bar=(212, 164, 32), shadow=False, t_out=E(lid)))
        film.add(Print(f"P{i + 2}", x, 600, 2200, rot=-1.5 + i, t_in=L(lid) + 0.3,
                       label=f"步骤{i + 1}截图", label_t=L(lid) + 0.6))
    film.add(Stamp("跑通", 0, 400, size=640, rot=-9, t_in=E(6) - 0.5))
    cam(0, 0, -600, 0.32, 0)
    for i, lid in enumerate((3, 4, 5)):
        cam(L(lid), (i - 1) * 4200, 0, 0.5, 0)
    cam(L(6), 0, 0, 0.2, 0)
    cam(doc.duration, 0, 0, 0.15, 0)
    film.fade_in, film.fade_out = 0.9, 2.0
    return film

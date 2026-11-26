# 传记类模板场景：照片沿时间线排开，红线串联，日期大字逐个落下。
# 年份写在 YEARS 里，与旁白顺序一致。
from engine import BigText, Film, Print, StringLine

YEARS = ["起点年份", "转折年份", "关键年份", "成名年份"]


def build_film(doc):
    L, E, W = doc.L, doc.E, doc.W
    film = Film(doc.duration, fps=30, look="wall")
    cam = film.cam
    xs = {1: -6900, 2: -2300, 3: 2300, 4: 6900}
    for i in (1, 2, 3, 4):
        lid = min(i + 1, 5)
        film.add(Print(f"P{i:02d}", xs[i], 0, 2400, rot=-1.5 + i * 0.8, t_in=L(lid) + 0.1,
                       label=YEARS[i - 1], label_t=L(lid) + 0.4))
        if i > 1:
            film.add(StringLine((xs[i - 1], -350), (xs[i], -350),
                                t_in=L(lid) - 0.2, dur=0.9, width=16, persist=True))
    film.add(BigText(YEARS[0], xs[1], -2300, 540, L(1) + 0.1,
                     rgb=(30, 26, 22), bar=(212, 164, 32), shadow=False, t_out=E(2)))
    cam(0, xs[1], 0, 0.5, 0)
    cam(L(3), xs[2], 0, 0.5, 0)
    cam(L(4), xs[3], 0, 0.5, 0)
    cam(L(5), xs[4], 0, 0.5, 0)
    cam(doc.duration, 0, 0, 0.13, 0)
    film.fade_in, film.fade_out = 0.9, 2.2
    return film

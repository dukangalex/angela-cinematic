# 竖屏模板（9:16）：构图骨架。竖屏不是把横屏裁窄，是把元素竖着排：
# 标题进顶部安全带、主图居中、结论章落下部安全带。坐标按 zoom 0.55、
# 1080x1920 的可见世界（宽约 6982、高约 12412）摆，安全带口径见
# engine/vertical.py 的 safe_insets（上 13%、下 20% 留给平台界面）。
# 定稿前把 SafeFrame 那行注释打开渲一张草稿帧核对，再关掉出正片。
from engine import BigText, Film, Print, Stamp
# from vertical import SafeFrame


def build_film(doc):
    L, E, W = doc.L, doc.E, doc.W
    film = Film(doc.duration, fps=30, look="wall")
    cam = film.cam
    film.add(BigText("竖屏标题", 0, -3600, 620, L(1) + 0.1, rgb=(238, 231, 214)))
    film.add(Print("P01", 0, -400, 4600, rot=-1.0, t_in=L(2) + 0.2,
                   label="主图说明", label_t=L(2) + 0.5))
    film.add(Stamp("结论", 1100, 1950, size=640, rot=-9, t_in=E(3) - 0.5))
    # film.add(SafeFrame(0, 0, 0.55, 1080, 1920))   # 草稿核对用，正片关掉
    cam(0, 0, 0, 0.55, 0)
    cam(L(2), 0, -300, 0.62, 0)
    cam(doc.duration, 0, 0, 0.5, 0)
    film.fade_in, film.fade_out = 0.9, 2.0
    return film

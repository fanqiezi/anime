import moefz
import milimili
import tmdm
import tkinter as tk
import multiprocessing

w = tk.Tk()
w.title("main")
# 调整窗口位置
SCREEN_WIDTH = w.winfo_screenwidth()  # 获取屏幕宽
SCREEN_HEIGHT = w.winfo_screenheight()  # 获取屏幕高
WIDTH = 500  # 窗口宽
HEIGHT = 500  # 窗口高
LEFT_OFFSET = (SCREEN_WIDTH - WIDTH) // 2  # 左右居中
TOP_OFFSET = (SCREEN_HEIGHT - HEIGHT) // 3  # 距离屏幕上边1/3
w.geometry("{0}x{1}+{2}+{3}".format(WIDTH, HEIGHT, LEFT_OFFSET, TOP_OFFSET))  # 窗口宽x窗口高+x轴偏移量+y轴偏移量
w.resizable(width=False, height=False)  # 不允许调整窗口宽高


def ok():
    tk.Label(w, text="输入番名:").place(x=5, y=50, anchor="nw")
    word = tk.Entry(w)
    word.place(x=68, y=50, anchor="nw")
    if variable.get() == "www.moefz.cc":
        tk.Button(w, text="搜索", command=lambda: moefz.search(w, word)).place(x=220, y=45, anchor="nw")
    elif variable.get() == "www.milimili.cc":
        tk.Button(w, text="搜索", command=lambda: milimili.search(w, word)).place(x=220, y=45, anchor="nw")
    elif variable.get() == "www.tmdm.tv":
        tk.Button(w, text="搜索", command=lambda: tmdm.search(w, word)).place(x=220, y=45, anchor="nw")


if __name__ == '__main__':
    tk.Label(w, text='源:').place(x=5, y=13, anchor="nw")
    # 下拉菜单
    OPTIONS = ["www.moefz.cc", "www.milimili.cc", "www.tmdm.tv"]  # etc
    variable = tk.StringVar(w)
    variable.set(OPTIONS[0])  # default value
    menu = tk.OptionMenu(w, variable, *OPTIONS)
    menu.place(x=30, y=5, anchor="nw")
    ok = tk.Button(w, text="OK", command=ok)
    ok.place(x=160, y=5, anchor="nw")
    multiprocessing.freeze_support()
    w.mainloop()

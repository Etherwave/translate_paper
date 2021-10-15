import tkinter as tk
from tkinter import *
from google_translate import google_translate
from youdao_translate import youdao_translate

global_refine_raw_data = ""
traslate_data = ""

translate_interval = 2000

def refine_pdf_raw_data(raw_data):
    '''
    因为pdf会有换行，一句话会断成两行，所以我们首先去除这些换行还有一个单词断开时的-。
    :param lines:
    :return:
    '''
    raw_data = raw_data.strip()
    if raw_data == "":
        return raw_data
    raw_data = raw_data.replace("-\n", " ")
    raw_data = raw_data.replace("\n", " ")
    return raw_data

def add_line_feed(ans):
    return ans.replace("。", "。\n\n")

def Adaptor(fun, **kwds):
    '''事件处理函数的适配器，相当于中介，那个event是从那里来的呢，我也纳闷，这也许就是python的伟大之处吧'''
    return lambda event, fun=fun, kwds=kwds: fun(event, **kwds)

def win_resize(event):
    global win, raw_text, translate_text
    '''事件处理函数'''
    win_width = win.winfo_width()
    win_height = win.winfo_height()
    text_width = int(win_width/14)
    text_height = int(win_height/14)
    raw_text.configure(width=text_width, height=text_height)
    translate_text.configure(width=text_width, height=text_height)

def refrash_translation():
    global win, global_refine_raw_data, raw_text, translate_text, traslate_data
    # 获取要翻译的数据
    raw_text_data = raw_text.get(0.0, END)
    # 去掉换行和词换行的-
    refine_raw_data = refine_pdf_raw_data(raw_text_data)
    # 如果数据与原来的不一样，那就翻译
    if refine_raw_data!=global_refine_raw_data or traslate_data=="something is wrong!":
        global_refine_raw_data = refine_raw_data
        traslate_data = google_translate(refine_raw_data)
        # traslate_data = youdao_translate(refine_raw_data)
        traslate_data = add_line_feed(traslate_data)
        # 先清空结果栏
        translate_text.delete(0.0, END)
        # 将答案输出到结果栏
        translate_text.insert('insert', traslate_data)
    win.after(translate_interval, refrash_translation)

def main():
    global win, raw_text, translate_text
    win = tk.Tk()
    win.title("翻译")
    # win.iconbitmap("/home/amzing/python/translate_paper/trans.ico")
    windows_width = int(win.winfo_screenwidth()/2)
    windows_height = int(win.winfo_screenheight()/2)
    win.resizable(True, True)
    win.geometry("{}x{}".format(windows_width, windows_height))

    frame1 = tk.Frame(win)
    frame1.pack(side=LEFT)
    frame2 = tk.Frame(win)
    frame2.pack(side=RIGHT)

    raw_text = tk.Text(frame1)
    raw_text.pack()

    translate_text = tk.Text(frame2)
    translate_text.pack()

    # bang
    win.bind('<Configure>', win_resize)
    win.after(translate_interval, refrash_translation)

    # 进入消息循环
    win.mainloop()





if __name__ == '__main__':
    main()
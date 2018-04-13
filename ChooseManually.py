# -*- coding: utf-8 -*-

"""
功能：读取路径下的jpg文件，自动打开(新建)TXT文件手动选择并保存合适的交通标志照片块
使用：
    (1)运行程序,点击 [选择图片] 按钮选取开始标记的图片 
    (2)鼠标中键拖动缩放图片
    (3)鼠标左键拖动选择合适的交通标志照片块的矩形方框
    (4)若选择合适，则单击鼠标右键保存，并显示下一张图片
    (5)[尺寸统一]功能将图片尺寸改为960*640，保存在当前目录下名为resize的文件夹
注意：
    (1)关于读写 txt 文件：可以直接在左侧栏修改，修改完毕后点击 [保存] 按钮即可
    (2)如果所选矩形不合适，在右键保存之前，重新选择即可
    (3)如果保存的数据不合适，在左侧栏删除，并点击[上一张]按钮重新选择即可
更新：
    (1)解决了图片读取出错的bug，文件夹里只能有图片的bug，矩形不能实时显示的bug
    (2)新增图片缩放功能
    (3)矩形方框颜色改为青色，宽度增加
    (4)新增操作说明
    (5)新增统一图片尺寸功能
"""

__Author__= 'Wang Fan' 
# __Date__: '2018-04-13'

import cv2
import numpy as np
import os
from tkinter import filedialog
import tkinter as tk
from PIL import ImageTk, Image




# ----------- Application Class ------------------
# ----------------- 窗口类 ----------------------
class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.pack(fill=tk.X)
        self.inidir = ''
        self.shape = []
        self.read_path = ''
        self.openfile = ''
        self.file_list = []
        self.myimage = {}
        self.msg = ""
        self.help = "使用说明：(1)运行程序,点击[选择图片]按钮选取开始标记的图片(2)鼠标中键拖动缩放图片(3)鼠标左键拖动选择合适的交通标志照片块的矩形方框(4)若选择合适，则单击鼠标右键保存，并显示下一张图片(5)[尺寸统一]功能将图片尺寸改为960*640，保存在当前目录下名为resize的文件夹"
        self.operation = [0,0,0]
        self.img = {}
        self.z = [0,0.2, 0.36, 0.488, 0.59, 0.67, 0.738, 0.79, 0.832, 0.866, 0.893, 0.91,0.94]
        self.ratio = 0
        self.pos_x = 0
        self.pos_y = 0
        self.pos_x1 = 0
        self.pos_y1 = 0
        self.pos_x2 = 0
        self.pos_y2 = 0
        self.start_picture = 0
        self.drawing = False
        self.save_path = self.read_path+'\\'
        self.txt_path = os.path.join(self.read_path, 'labels.txt')
        self.createWidgets()

    def createWidgets(self):
        self.seButton = tk.Button(self, text='选择图片', command=self.getfile)
        self.seButton.pack(side=tk.LEFT, padx=2, pady=2)
        self.saveButton = tk.Button(self, text='保存', command=self.savefile)
        self.saveButton.pack(side=tk.LEFT, padx=2, pady=2)
        self.reButton = tk.Button(self, text='尺寸统一', command=self.resizeimg)
        self.reButton.pack(side=tk.LEFT, padx=2, pady=2)

        self.midframe = tk.Frame(None)
        self.midframe.pack(padx=2, pady=2)

        self.leftframe = tk.Frame(self.midframe)
        self.leftframe.pack(side=tk.LEFT, padx=2, pady=2)
        self.scroll = tk.Scrollbar(self.leftframe)
        self.scroll.pack(side=tk.RIGHT, fill=tk.Y, padx=2, pady=2)
        self.textPad = tk.Text(self.leftframe, undo=True, width=30, height=540)
        self.textPad.config(yscrollcommand=self.scroll.set)
        self.textPad.pack(side=tk.LEFT, padx=2, pady=2)
        self.scroll.config(command=self.textPad.yview)

        self.rightframe = tk.Frame(self.midframe)
        self.rightframe.pack(side=tk.RIGHT, padx=2, pady=2)
        self.Mes = tk.Message(self.rightframe,text=self.help,width=960)
        self.Mes.pack(side=tk.TOP)
        self.rtframe = tk.Frame(self.rightframe)
        self.rtframe.pack(side=tk.TOP)
        self.lastButton = tk.Button(
            self.rtframe, text='上一张', command=self.lastimage)
        self.lastButton.pack(side=tk.LEFT, padx=2, pady=0)
        self.nextButton = tk.Button(
            self.rtframe, text='下一张', command=self.nextimage)
        self.nextButton.pack(side=tk.LEFT, padx=2, pady=0)
        self.mycanvas = tk.Canvas(
            self.rightframe, width=960, height=640, cursor='crosshair')
        self.mycanvas.pack(padx=2, pady=2)
        self.mycanvas.bind("<B1-Motion>", self.rectlocation)
        self.mycanvas.bind("<Button-1>", self.draw_rect)
        self.mycanvas.bind("<Button-3>", self.save_result)
        self.mycanvas.bind("<MouseWheel>", self.processWheel)

        self.status = tk.Label(self.rightframe, text='状态栏',
                               bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status.pack(side=tk.BOTTOM, fill=tk.X, pady=2)
        self.status1 = tk.Label(
            self.rightframe, text='地址栏', bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status1.pack(side=tk.BOTTOM, fill=tk.X, pady=2)

    def nextimage(self):
        self.start_picture += 1
        self.openfile = os.path.join(
            self.read_path, self.file_list[self.start_picture])
        img = cv2.imdecode(np.fromfile(self.openfile, dtype=np.uint8), -1)
        self.img = cv2.resize(img, (960, 640), cv2.INTER_LINEAR)
        self.showimage(self.img)
        self.ratio = 0
        self.operation = [0,0,0]
        self.status1.config(text=self.openfile)

    def rectlocation(self, event):
        self.mycanvas.delete('r')
        x = event.x * (1-self.operation[2])+self.operation[0]
        y = event.y * (1-self.operation[2])+self.operation[1]
        self.pos_x2 = int(x)
        self.pos_y2 = int(y)
        self.status.config(text=(self.pos_x2, self.pos_y2))
        self.mycanvas.create_rectangle(
            self.pos_x, self.pos_y, event.x, event.y, outline='cyan',width=2,tags='r')

    def draw_rect(self, event):
        x = event.x * (1-self.operation[2])+self.operation[0]
        y = event.y * (1-self.operation[2])+self.operation[1]
        self.pos_x = event.x
        self.pos_y = event.y
        self.pos_x1 = int(x)
        self.pos_y1 = int(y)
        self.status.config(text=(self.pos_x1, self.pos_y1))

    def save_result(self, event):
        _,name = os.path.split(self.openfile)
        self.msg = name + ' '+str(self.pos_x1) + ' '+str(self.pos_y1)
        self.msg = self.msg + ' '+str(self.pos_x2-self.pos_x1)+' '
        self.msg = self.msg + str(self.pos_y2-self.pos_y1)+'\n'
        self.textPad.insert(tk.END, self.msg)
        self.savefile()
        self.ratio = 0
        self.operation = [0,0,0]
        self.start_picture += 1
        self.openfile = os.path.join(
            self.read_path, self.file_list[self.start_picture])
        img = cv2.imdecode(np.fromfile(self.openfile, dtype=np.uint8), -1)
        self.img = cv2.resize(img, (960, 640), cv2.INTER_LINEAR)
        self.showimage(self.img)
        self.status1.config(text=self.openfile)

    def resizeimg(self):
        if self.shape[0] == 640 and self.shape[1] == 960:
            self.status.config(text='图片尺寸已经是960*640')
        else:
            self.repath = os.path.join(self.read_path,'resize')
            if not os.path.isdir(self.repath):
                os.makedirs(self.repath)
            for filename in self.file_list:
                tpath = os.path.join(self.read_path,filename)
                img = Image.open(tpath)
                img = img.resize((960,640),Image.ANTIALIAS)
                npath = os.path.join(self.repath,filename)
                img.save(npath)
            self.inidir = self.repath
            self.status.config(text='已完成统一尺寸，请重新选择图片')
            self.getfile()
    
    def getfile(self):
        ftypes = (('所有文件', "*"),('JPG 图片', '*.jpg'),('PNG 图片', '*.png'))
        self.openfile = filedialog.askopenfilename(
            initialdir=self.inidir, filetypes=ftypes,title='请选择图片')
        if self.openfile:
            self.read_path = os.path.dirname(self.openfile)
            self.save_path = self.read_path+'\\'
            self.txt_path = os.path.join(self.read_path, 'labels.txt')
            file_list1 = os.listdir(self.read_path)
            for filename in file_list1:
                if '.jpg' in filename or '.png' in filename:
                    self.file_list.append(filename)
            self.file_list.sort()
            _,imagename = os.path.split(self.openfile)
            self.start_picture = self.file_list.index(imagename)
            img = cv2.imdecode(np.fromfile(self.openfile, dtype=np.uint8), -1)
            self.shape = img.shape
            self.status.config(text=('图片尺寸为是',self.shape[1],'x',self.shape[0]))
            self.img = cv2.resize(img, (960, 640), cv2.INTER_LINEAR)
            self.showimage(self.img)
            self.status1.config(text=self.openfile)
            self.textPad.delete(1.0, tk.END)
            try:
                f = open(self.txt_path, 'r')
                self.textPad.insert(1.0, f.read())
                f.close()
            except:
                self.textPad.delete(1.0, tk.END)

    def savefile(self):
        with open(self.txt_path, 'w') as f:
            msg = self.textPad.get(1.0, tk.END)
            f.write(msg)
            self.status.config(text='保存成功')

    def showimage(self, img):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        self.myimage = ImageTk.PhotoImage(img)
        self.mycanvas.create_image(0, 0, anchor=tk.NW, image=self.myimage)

    def lastimage(self):
        self.start_picture -= 1
        self.openfile = os.path.join(
            self.read_path, self.file_list[self.start_picture])
        img = cv2.imdecode(np.fromfile(self.openfile, dtype=np.uint8), -1)
        self.img = cv2.resize(img, (960, 640), cv2.INTER_LINEAR)
        self.showimage(self.img)
        self.status1.config(text=self.openfile)
        self.ratio = 0
        self.operation = [0,0,0]

    def processWheel(self, event):
        if event.delta == -120:
            self.ratio -= 1
        if event.delta == 120:
            self.ratio += 1
        if self.ratio >= len(self.z):
            self.ratio = 0
        x = event.x * (1-self.operation[2])+self.operation[0]
        y = event.y * (1-self.operation[2])+self.operation[1]
        x1 = int(x*self.z[self.ratio])
        y1 = int(y*self.z[self.ratio])
        x2 = int((x-x1)*960/x + x1)
        y2 = int((y-y1)*640/y + y1)
        newimg = self.img[y1:y2, x1:x2]
        newimg = cv2.resize(newimg, (960, 640), cv2.INTER_LINEAR)
        self.operation = [x1,y1,self.z[self.ratio]]
        self.showimage(newimg)



# --------------- main project  ------------------
# ------------------- 主程序 -----------------
if __name__ == '__main__':
    app = Application()
    app.master.title('标注')
    app.master.geometry('1260x860+0+0')
    app.mainloop()

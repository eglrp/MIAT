# -*- coding:utf-8 -*-
import xlrd
import os
import cv2
import shutil

""" 
功能：
    1.读取 path 路径下所有的 xxx.avi 和 readme.xls 文件
    2.将 xxx.avi 转换为图片保存在该目录下的 images 文件夹中
    3.根据 readme.xls 内容，在 outpath 路径下创建对应交通标志的文件夹
    4.将图片和对应的标注放到对应的文件夹中
使用：
    1.修改 path 和 outpath 两个路径
    2.运行程序
注意：
    1. path 路径不能包含中文
"""

path = r'C:\Users\admin\Desktop\Excel'
outpath = r'C:\Users\admin\Desktop\Excel\result'


result_xls = []
result_avi = []


#功能：拷贝图片
def copy(src, dst):
    nums = []
    number = 0
    if not os.path.isdir(dst):
        os.makedirs(dst)
    else:
        dstnames = os.listdir(dst)
        for dstname in dstnames:
            num, _ = os.path.splitext(dstname)
            if not 'labels' in num:
                nums.append(int(num))
        if nums:
            number = max(nums)
    names = os.listdir(src)
    errors = []
    for name in names:
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if os.path.exists(dstname):
                num, _ = os.path.splitext(name)
                num = int(num)+number
                dstname = os.path.join(dst, str(num)+'.jpg')
                shutil.copy2(srcname, dstname)
            else:
                shutil.copy2(srcname, dstname)
        except (IOError, os.error) as why:
            errors.append((srcname, dstname, str(why)))
        except OSError as err:
            errors.extend(err.args[0])
    try:
        shutil.copystat(src, dst)
    except WindowsError:
        pass
    except OSError as why:
        errors.extend((src, dst, str(why)))
    if errors:
        raise OSError(errors)
    return number


#功能：寻找文件目录下的Excel与Avi 文件
def Path_Seek():
    stack = []                                                          #存取目录栈      
    filenames = []                                                      #用文件名判断类型
    if os.path.exists(path):
        stack.append(path)
    else:
        return 0
    while len(stack) != 0:
        path2 = stack.pop()
        if os.path.isdir(path2):
            filenames = os.listdir(path2)
            for name in filenames:
                mPath = os.path.join(path2, name)
                if os.path.isdir(mPath):                                #目录入栈
                    stack.append(mPath)
                elif name == 'readme.xls':                              #非目录加入xls或avi全局列表
                    result_xls.append(mPath)
                elif '.avi' in name:
                    result_avi.append(mPath)
    return 1


#功能：读取Excel文件内容，并拷贝图片
def Excel_Transform_TXT(mypath):
    try:
        workbook = xlrd.open_workbook(mypath)
    except Exception as e:
        print(str(e))
    sheet1 = workbook.sheet_by_index(0)
    num = sheet1.cell_value(1, 1)                                       #标识数量                                
    for m in range(int(num)):
        name = sheet1.cell_value(1, 7*m+2)
        path2 = os.path.join(outpath, name.strip())
        src, _ = os.path.split(mypath)
        src = os.path.join(src, 'images')
        number = copy(src, path2)                                       #拷贝图片
        with open(path2+'\\labels.txt', 'a') as f:
            for n in range(1, sheet1.nrows):
                row = sheet1.row_values(n)                              #每行的所有数值    
                if row:
                    app = []
                    app.append(str(int(row[0])+number) + '.jpg')
                    app.append(str(int(row[5+7*m]*960/1280)))           #修改数据尺寸
                    app.append(str(int(row[6+7*m]*640/1024)))
                    app.append(str(int(row[7+7*m]*960/1280))) 
                    app.append(str(int(row[8+7*m]*640/1024)))

                    f.write(' '.join(app) + '\n')
            print(src+' 图片拷贝完成')


#功能：切分视频输出到当前文件夹
def Video_Transform_Image(path):
    vc = cv2.VideoCapture(path)                                         #逐帧读取视频
    outdir = os.path.split(path)
    outpath = os.path.join(outdir[0], 'images')
    os.makedirs(outpath)

    ordernum = 1
    while(1):
        ret, frame = vc.read()
        if ret is False:
            break
        frame = cv2.resize(frame, (960, 640), interpolation=cv2.INTER_AREA)     #修改输出图片为960*640
        cv2.imwrite(outpath+'//'+str(ordernum)+'.jpg', frame)
        ordernum = ordernum+1
        if cv2.waitKey(1) &  0xFF == ord('q'):
            break

    vc.release()
    print(path, r' 转换成图片')
    


def main():
    i = Path_Seek()
    if i:
        for m in result_avi:
            t, _ = os.path.split(m)
            t = os.path.join(t, 'images')
            if not os.path.exists(t):
                Video_Transform_Image(m)
            else:
                print(m, r' 图片已存在')
        for n in result_xls:
            Excel_Transform_TXT(n)
    else:
        print('路径不存在！')


if __name__ == '__main__':
    main()

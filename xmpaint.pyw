#coding=utf-8
import sys
if sys.version[0]=='2':
    pass
    #os.system('start c:/python34/pythonw.exe '+sys.argv[0])
 #   sys.exit(-1)

from tkinter import *
from tkinter import font
from tkinter import messagebox
from tkinter.ttk import *
import subprocess
import threading
import time
import os

def buildraw(*_):
    compiler=compilervar.get()
    lines=[]
    hllines=[]
    global img
    global canvasimg
    starttime=time.time()
    dir=directed.get()=='yes'
    
    #interpret
    tk.title('Interpreting data...')
    for data in hlin.get(1.0,END).split('\n'):
        if data:
            splited=data.split(' ')
            if len(splited)==2:
                hllines.append(splited)
            elif len(splited)==1:
                lines.append('"%s"[color="black",fillcolor="greenyellow",style="bold,filled"];\n'%\
                    splited[0].replace('\\',' ').replace('"','\\"'))
            else:
                messagebox.showerror('Error','Syntax error in highlight "%s"'%data)
    
    for data in textin.get(1.0,END).split('\n'):
        if not data:
            continue
        splited=data.split()
        for now in range(len(splited)):
            splited[now]=splited[now].replace('\\',' ').replace('"','\\"')
        if len(splited)==3:
            fstr='"%s"->"%s"'%tuple(splited[:2]) if dir else '"%s"--"%s"'%tuple(splited[:2])
            if [splited[0],splited[1]] in hllines:
                lines.append(fstr+'[label="%s",color="red",style="bold,filled"];\n'%splited[2])
            else:
                lines.append(fstr+'[label="%s"];\n'%splited[2])
        elif len(splited)==2:
            fstr='"%s"->"%s"'%tuple(splited) if dir else '"%s"--"%s"'%tuple(splited)
            if [splited[0],splited[1]] in hllines:
                lines.append(fstr+'[color="red",style="bold,filled"];\n')
            else:
                lines.append(fstr+';\n')
        else:
            messagebox.showerror('Error','Syntax error in line "%s"'%data)
            return
            

    #write
    if not os.path.exists('output'):
        os.mkdir('output')
    tk.title('Writing graph file...')
    try:
        with open('output/out.gv','w') as f:
            f.write('%s A{\n'%('digraph' if dir else 'graph'))
            for a in lines:
                f.write(a)
            f.write('}')
    except Exception as e:
        messagebox.showerror('Error','Can\'t write file: %s'%e)
        return

    #build
    tk.title('Building graph file...')
    if not os.path.isfile('compiler/%s.exe'%compiler):
        messagebox.showerror('Error','Can\'t find %s compiler'%compiler)
        return
    exe=subprocess.Popen(
        '"compiler/%s.exe" output/out.gv -o output/out.png -Tpng'%compiler,
        shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout,stderr=exe.communicate()
    code=exe.wait()
    if code!=0:
        return messagebox.showerror('Error','Compiler returned %d.\n\nSTDOUT:\n%s\n\nSTDERR:\n%s'%(
            code,
            stdout.decode(encoding='gbk',errors='ignore'),
            stderr.decode(encoding='gbk',errors='ignore'),
        ))
    #log(stdout.decode(encoding='gbk',errors='ignore'),'output')
    #log(stderr.decode(encoding='gbk',errors='ignore'),'output')

    #display
    tk.title('Loading image...')
    try:
        img=PhotoImage(file='output/out.png')
    except Exception as e:
        messagebox.showerror('Error','Can\'t display image: %s'%e)
        return

    if canvasimg:
        canvas.delete(canvasimg)
    midwidth=canvas.winfo_width()//2
    midheight=canvas.winfo_height()//2
    imgwidth=img.width()
    imgheight=img.height()
    tk.title('Redrawing canvas...')
    canvas['scrollregion']=(
        midwidth-imgwidth/2-20,midheight-imgheight/2-20,
        midwidth+imgwidth/2+20,midheight+imgheight/2+20)
    canvasimg=canvas.create_image(\
        midwidth,midheight,anchor=CENTER,image=img)

    #cleanup
    if shouldCleanup.get()=='yes':
        tk.title('Cleaning up...')
        try:
            os.remove('output/out.gv')
            os.remove('output/out.png')
        except OSError as e:
            messagebox.showerror('Error','Can\'t remove temp file: %s'%e)
            return

def build(*_):
    def mybuild():
        global building
        building=True
        buildbtn['state']='disabled'
        try:
            buildraw()
        except Exception as e:
            messagebox.showerror('Error','Unhandled exception: %r'%e)
            raise
        finally:
            tk.title('XMPaint')
            building=False
            buildbtn['state']='normal'

    if building:
        return
    t=threading.Thread(target=mybuild,args=())
    t.setDaemon(True)
    t.start()

def startmove(event):
    global movex
    global movey
    movex,movey=event.x,event.y

def moving(event):
    global movex
    global movey
    canvas.xview_scroll(movex-event.x,'units')
    canvas.yview_scroll(movey-event.y,'units')
    movex,movey=event.x,event.y

tk=Tk()
tk.geometry('900x600')
tk.title('XMPaint')
tk.rowconfigure(0,weight=1)
tk.columnconfigure(2,weight=1)
tk.bind_all('<F5>',build)
compilervar=StringVar(value='dot')
directed=StringVar(value='yes')
shouldCleanup=StringVar(value='yes')
building=False

#text in
textframe=Frame(tk)
textframe.grid(row=0,column=0,sticky='NSWE')
textframe.columnconfigure(0,weight=1)

textin=Text(textframe,font='Consolas',width=20,bg='#CCCCFF')
textin.grid(row=0,column=0,sticky='NSWE')
textin_sbar=Scrollbar(textframe,orient=VERTICAL,command=textin.yview)
textin_sbar.grid(row=0,column=1,sticky='NS')
textin['yscrollcommand']=textin_sbar.set
textframe.rowconfigure(0,weight=1)

hlin=Text(textframe,font='Consolas -13',width=20,height=9,bg='#FFCCCC')
hlin.grid(row=1,column=0,sticky='NSWE')
hlin_sbar=Scrollbar(textframe,orient=VERTICAL,command=hlin.yview)
hlin_sbar.grid(row=1,column=1,sticky='NS')
hlin['yscrollcommand']=hlin_sbar.set

#canvas
imgframe=Frame(tk)
imgframe.grid(row=0,column=2,rowspan=2,sticky='NSWE')
imgframe.grid_columnconfigure(0,weight=1)
imgframe.grid_rowconfigure(0,weight=1)

img=PhotoImage()
canvasimg=None

imgh=Scrollbar(imgframe,orient=HORIZONTAL)
imgv=Scrollbar(imgframe,orient=VERTICAL)
canvas=Canvas(imgframe,yscrollcommand=imgv.set,xscrollcommand=imgh.set,
              xscrollincrement='1',yscrollincrement='1')
canvas.configure(background='#FFFFFF')
imgh['command']=canvas.xview
imgv['command']=canvas.yview
canvas.grid(column=0,row=0,sticky='NSWE')
imgh.grid(column=0,row=1,sticky='WE')
imgv.grid(column=1,row=0,sticky='NS')

movex,movey=0,0
canvas.bind("<Button-1>", startmove)
canvas.bind("<B1-Motion>", moving)

#config frame
frame=Frame(tk)
frame.grid(row=1,column=0,columnspan=2)
Combobox(frame,textvariable=compilervar,values=('dot','fdp','sfdp','circo'),width=10)\
    .grid(row=0,column=0,pady=2,padx=2)
buildbtn=Button(frame,text='生成 (F5)',command=build)
buildbtn.grid(row=0,column=1)
Checkbutton(frame,text='清理临时文件',variable=shouldCleanup,onvalue='yes',offvalue='no')\
    .grid(row=2,column=0)
Checkbutton(frame,text='有向图',variable=directed,onvalue='yes',offvalue='no')\
    .grid(row=2,column=1)

mainloop()
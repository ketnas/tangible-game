#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 25 11:28:02 2019

@author: Kejkaew
"""

from tkinter.constants import E, RIGHT
from interface.element import setDropdown,setBlock
from imageProcess.colorDetection import imagePlay
from imageProcess.recordVideo import realTime
import numpy as np
import tkinter.filedialog
import tkinter.ttk
import tkinter as tk
import os
    
class mainGame:
    def __init__(self):
        self.window = tk.Tk()
        # self.window.geometry("500x500")
        self.window.resizable(False,False)
        self.window.title("Tangible Game 1.2")
        self.my_object = []
        
        #top label
        self.lbl_frame = tk.Frame(self.window)
        self.lbl_frame.pack(side="top",fill=tk.X)
        # lbl = tk.Label(self.lbl_frame,text="Please select an input type"+"\n Please enter your name and \n set depth of each block",
        #                font = "Helvetica 16 bold")
        lbl = tk.Label(self.lbl_frame,text="Please select a task",font = "Helvetica 16 bold")
        
        lbl.pack(pady= 10)

        self.entryframe = tk.Frame(self.lbl_frame)
        self.entryframe.pack(pady = 10,padx=10,fill=tk.X)
        
        ##fram 1, row 0
        #create task type drowdown
        lbl1 = tk.Label(self.entryframe,text="Task : ",font = "Helvetica 14 bold")
        lbl1.grid(pady = 5,row=0,column=0)
        self.tkvar = tk.StringVar(self.window)
        # link function to change dropdown
        self.tkvar.trace('w', self.change_inputtype)
        # Dictionary with options
        choices = {"Analysis","Recording"}
        
        self.popupMenu = tk.OptionMenu(self.entryframe ,self.tkvar, *choices)
        self.popupMenu.grid(pady = 5,sticky="W",row = 0, column =1)
        menu = self.popupMenu.nametowidget(self.popupMenu.menuname)
        menu.configure(font=('Helvetica', 14))

        ## browse video file
        self.button_file = tk.Button(self.entryframe,text = "Select video file",command = self.browseFile,font = "Helvetica 14 bold")
        self.button_file.grid(padx = (50,5), row =0, column=2)
        # self.lbl1 = tk.Label(self.entryframe1,text="Video input file",font = "Helvetica 14")
        # self.lbl1.grid(row=0,column=3)
        self.videoentry = tk.Entry(self.entryframe,width = 10,state="disabled")
        self.videoentry.grid(pady = 5,row =0,column =3)

        # set default option after create button_file object
        self.tkvar.set("Analysis") # set the default option
        # Seperator object
        separator = tkinter.ttk.Separator(self.window, orient='horizontal')
        separator.pack(fill = tk.X)
        
        ##frame 2, row 0
        #create textbox for user's name 
        self.lbl_frame = tk.Frame(self.window)
        self.lbl_frame.pack(pady = 10, fill=tk.X)
        lbl = tk.Label(self.lbl_frame,text="Please enter your code and output filename",font = "Helvetica 16 bold")
        lbl.pack(pady= 10)
        self.entryframe = tk.Frame(self.lbl_frame)
        self.entryframe.pack(pady = 10,padx=10,fill=tk.X)

        lbl1 = tk.Label(self.entryframe,text="Your code: ",font = "Helvetica 14 bold")
        lbl1.grid(pady = 5,sticky="W",row=0,column=0)
        self.entry = tk.Entry(self.entryframe,width = 10)
        self.entry.grid(pady = 5,row =0,column =1)
        
        ## output file
        lbl1 = tk.Label(self.entryframe,text="Output file : ",font = "Helvetica 14 bold")
        lbl1.grid(pady = 5,row=0,column=2)
        self.outputentry = tk.Entry(self.entryframe,width = 10)
        self.outputentry.grid(pady = 5,row =0,column =3)
        
        # Seperator object
        separator = tkinter.ttk.Separator(self.window, orient='horizontal')
        separator.pack(fill = tk.X)

        #frame 3 row 0
        self.lbl_frame = tk.Frame(self.window)
        self.lbl_frame.pack(fill=tk.X)
        lbl = tk.Label(self.lbl_frame,text="Please set depth of each block and game condition",font = "Helvetica 16 bold")
        lbl.pack(pady= 10)

        ## Add a frame for set depth drowdown automatically
        self.depthdrop = tk.Frame(self.lbl_frame)
        self.depthdrop.pack(pady = 10,padx=10,fill=tk.X)
        
        ##row 0
        #create input type drowdown and condition
        lbl1 = tk.Label(self.depthdrop,text="Block depth group : ",font = "Helvetica 14 bold")
        lbl1.grid(pady = 5,row=0,column=0)
        self.tkvar1 = tk.StringVar(self.window)
        # link function to change dropdown
        self.tkvar1.trace('w', self.change_depth)
        # Dictionary with options
        choices1 = {"A","B","C"}
        self.aa = [1,1,1,1,1,7,5,1,9,3,3,1,9,7,5]
        self.bb = [1,1,1,1,1,3,1,9,7,5,7,5,1,9,3]
        self.cc = [1,1,1,1,1,1,3,5,7,9,3,1,9,7,5]
        
        
        self.popupMenu1 = tk.OptionMenu(self.depthdrop ,self.tkvar1, *sorted(choices1))
        
        self.popupMenu1.grid(pady = 5,sticky="W",row = 0, column =1)
        menu = self.popupMenu1.nametowidget(self.popupMenu1.menuname)
        menu.configure(font=('Helvetica', 14))
        
        ## condition
        lbl1 = tk.Label(self.depthdrop,text="Game condition : ",font = "Helvetica 14 bold")
        lbl1.grid(pady = 5,row=0,column=2)
        self.condition = tk.StringVar(self.window)
        # Dictionary with options
        choices1 = {"Equal-all","Equal-row","Equal-column"}
        self.condition.set("Equal-all")
        
        self.popupMenu2 = tk.OptionMenu(self.depthdrop ,self.condition, *choices1)
        
        self.popupMenu2.grid(pady = 5,sticky="W",row = 0, column =3)
        menu = self.popupMenu2.nametowidget(self.popupMenu2.menuname)
        menu.configure(font=('Helvetica', 14))
        
        
        # Add a frame for set depth dropdown 
        self.mainframe = tk.Frame(self.window)
        self.mainframe.pack(pady = 10,padx=100,fill=tk.X)
        
        for i in range(3):
            for j in range(5):
                self.my_object.append(setDropdown(self.window,self.mainframe,i*5+j,i,j))
            
        # Add a frame for bottom OK
        self.bottomframe = tk.Frame(self.window)
        self.bottomframe.pack(side="bottom",padx=20,pady=20)
        okBtn = tk.Button(self.bottomframe, text = "OK",
                          command=lambda: self.startGame(),font = "Helvetica 16")
        okBtn.pack(padx=20,pady=5,ipady=5,ipadx=5,fill=tk.X)
        
        ## cheat setting
        self.videoentry.configure(state="normal")
        self.videoentry.insert(0,"t.avi")
        self.videoentry.configure(state="disabled")
        self.outputentry.insert(0,"testfile13-11")
        self.tkvar1.set('A')
        self.entry.insert(0,"Test")
        
        self.window.mainloop()
        
    def browseFile(self,*args):
        filename = tkinter.filedialog.askopenfilename(initialdir = ".",
                                          title = "Select a File",
                                          filetypes = (("Video files",
                                                        "*.avi"),
                                                       ("all files",
                                                        "*.*")))
        
        filen = os.path.basename(filename)
        self.videoentry.configure(state="normal")
        self.videoentry.insert(0,filen)
        self.videoentry.configure(state="disabled")
        # self.lbl1.configure(text=filen)

    def change_inputtype(self,*args):
        print(self.tkvar.get())
        inputt = self.tkvar.get()
        if inputt == "Analysis":
            # self.videoentry.configure(state="normal")
            self.button_file.configure(state = "normal")
        else:
            # self.videoentry.configure(state = "disabled")
            self.button_file.configure(state = "disabled")
            
    def change_depth(self,*args):
        print(self.tkvar1.get())
        deptht = self.tkvar1.get()
        depth = []
        if deptht == 'A':
            depth = self.aa
        elif deptht == 'B':
            depth = self.bb
        else:
            depth = self.cc
        for i in range(len(depth)):
            self.my_object[i].set_dropdown(depth[i])
        

    #playmode,my_object,entry,entryframe,window,mainframe,lbl_frame,bottomframe
    def startGame(self):
        print("start")
        
        self.playmode = self.tkvar.get()
        self.cond = self.condition.get()
        self.videofile = self.videoentry.get()
        self.outfile = self.outputentry.get()
        
        self.depth_list = []
        for i in range(len(self.my_object)):
            deep, num = self.my_object[i].get_dropdown()
            self.depth_list.append(deep)
    
        print(self.depth_list)
                
        name = self.entry.get()
        # self.entryframe.destroy()
        # self.lbl_frame.destroy()
        # self.mainframe.destroy()
        # self.depthdrop.destroy()
        # self.bottomframe.destroy()
        self.window.destroy()

        self.showCells()
        
        if self.playmode == "Analysis":
            self.imageplay= imagePlay(name,self.outfile,self.my_obj,self.window,self.playmode,self.depth_list,self.cond,self.timelbl,self.videofile)
            self.imageplay.cheatingFun()
        else:
            self.imageplay = realTime(name,self.outfile,self.window)
            self.imageplay.startRecord()
        
    def showCells(self):
        self.window = tk.Tk()
        # self.window.geometry("500x500")
        self.window.resizable(False,False)
        self.window.title("Tangible Game 1.2")

        self.lbl_frame = tk.Frame(self.window,relief="raised",borderwidth=2)
        self.lbl_frame.pack(side="top",fill=tk.X)
        lbl = tk.Label(self.lbl_frame,text="Play game! : "+self.playmode,font = "Helvetica 16 bold")
        lbl.pack(pady= 10)

        if self.playmode == "Analysis":
            self.timeframe = tk.Frame(self.window)
            self.timeframe.pack(padx=10,anchor = "e")
            self.timelbl = tk.Label(self.timeframe,text="Time: 0.0 seconds Analysis: 0%",font = "Helvetica 12 bold")
            self.timelbl.pack()

            self.mainframe = tk.Frame(self.window)
            self.mainframe.pack(pady = 10,padx=10)
            s_posx = np.array(range(100,400,60))
            s_posy = np.array(range(50,230,60))
            e_posx = np.array(range(150,450,60))
            e_posy = np.array(range(100,230,60))
            
            s_posx = np.tile(s_posx,reps=3)
            s_posy = np.repeat(s_posy,5)
            e_posx = np.tile(e_posx,reps=3)
            e_posy = np.repeat(e_posy,5)
            
            # creating the 'Canvas' area of width and height 500px
            self.canvas = tk.Canvas(self.mainframe,width = 470,height = 250)
            self.canvas.pack()
            self.my_obj = []
            for i in range(3):
                for j in range(5):
                    num = i*5+j
                    # setBlock is a class that will be used in another class
                    self.my_obj.append(setBlock(self.canvas,num,s_posx[num],s_posy[num],e_posx[num],e_posy[num]))
            
            self.bottomframe = tk.Frame(self.window)
            self.bottomframe.pack(side="bottom",padx=20,pady=20)
            okBtn = tk.Button(self.bottomframe, text = "EXIT",command=lambda: self.exitGame(),
                            font = "Helvetica 16")
            okBtn.pack(padx=20,pady=5,ipady=5,ipadx=5,fill=tk.X)
        else:
            self.bottomframe = tk.Frame(self.window)
            self.bottomframe.pack(side="bottom",padx=20,pady=20)
            okBtn = tk.Button(self.bottomframe, text = "Stop Recording",command=lambda: self.exitGame(),
                            font = "Helvetica 16")
            okBtn.pack(padx=20,pady=5,ipady=5,ipadx=5,fill=tk.X)
        
    def exitGame(self):
        #print("stop")
        self.imageplay.stopImage()
        self.window.destroy()
        
    
    

## main program, it needs 2 required flags, which are -v (video) with file or -r (realtime) 
## and condition -c [option: e-all,e-row,e-col,d-row]
if __name__ == '__main__':
    obj = mainGame()
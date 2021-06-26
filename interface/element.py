#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 21 14:00:16 2019

@author: Kejkaew
"""

import tkinter as tk

class setDropdown:
    def __init__(self,window,frame,num,prow,pcol):
        self.frame = frame
        self.num = num
        # Create a Tkinter variable
        self.tkvar = tk.StringVar(window)
        # link function to change dropdown
        self.tkvar.trace('w', self.change_dropdown)
        # Dictionary with options
        choices = { '1','3','5','7','9'}
        self.tkvar.set('1') # set the default option
        self.popupMenu = tk.OptionMenu(self.frame ,self.tkvar, *sorted(choices))
        
        self.popupMenu.grid(row = prow, column =pcol)
        menu = self.popupMenu.nametowidget(self.popupMenu.menuname)
        menu.configure(font=('Helvetica', 16))
        
    # on change dropdown value
    def change_dropdown(self,*args):
        print(self.tkvar.get(),self.num)
        
    def get_dropdown(self):
        return(self.tkvar.get(),self.num)
        
    def set_dropdown(self,value):
        self.tkvar.set(value)
        
class setBlock:
    def __init__(self,canvas,num,sx,sy,ex,ey):
        
        # 'create_rectangle' is used to create rectangle. Parameters:- (starting x-point, starting y-point, width, height, fill)
        # starting point the coordinates of top-left point of rectangle
        self.num = num
        self.sx = sx
        self.sy = sy
        self.ex = ex
        self.ey = ey
        self.canvas = canvas
        self.rect = self.canvas.create_rectangle(self.sx,self.sy,self.ex,self.ey, fill = "white")

    def change_fill(self):
        #print("change")
        #rect = self.canvas.create_rectangle(self.sx,self.sy,self.ex,self.ey, fill = "green")
        self.canvas.itemconfig(self.rect,fill='red')
        
    def change_nofill(self):
        #print("change")
        #rect = self.canvas.create_rectangle(self.sx,self.sy,self.ex,self.ey, fill = "white")
        self.canvas.itemconfig(self.rect,fill='white')

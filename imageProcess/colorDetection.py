#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 21 14:17:01 2019

@author: Kejkaew
"""

from pyimagesearch.transform import four_point_transform
from pyimagesearch.shapedetector import ShapeDetector
from handDetect.handDetection import handDetection
from filevideostream import FileVideoStream
import numpy as np
import pandas as pd
import cv2
import datetime,time

import signal
import sys
from tkinter import messagebox
    
def chooseMax(arr):
    unique1 = np.unique(arr,return_counts=True)
    max_value = unique1[0][np.argmax(unique1[1])]
    return(max_value)
    
def setColorShape(): 
    data = {"color_low" :[(0,120,100),(93,90,72),(20,170,125),(60,90,63)]*2,  #HSV
                        "color_up" :[(10,255,255),(114,200,255),(40,255,255),(90,255,255)]*2,
                        "color" :["red","blu","yel","gre"]*2,
                        "col_code": [(0,0,255),(255,0,0),(0,255,0),(21,169,21)]*2, ##BGR not HSV
                        "shape_1" : np.repeat(np.array([0,1]),4),
                        "length" : [5,9,7,0,13,-22,3,11]}
                       # "length" : np.linspace(1,9,num = 8,dtype=int)}
    data_grid = pd.DataFrame.from_dict(data=data)
    #(200 < df.x +30) & (300 < df.y+30)
    return(data_grid)
    
class imagePlay:
    def __init__(self,name,outputfile,rect,window,playmode,depth,cond,timelbl,videofile=None):
        # click points used for crop image

        self.circles = []
        self.counts = 0
        self.rect = rect
        # self.canvas = canvas
        self.window = window
        self.name = name
        self.cond = cond
        self.outputfile = outputfile
        self.timelbl = timelbl
        self.timestart = time.time()
        
        self.nGrid = 15
        self.ncolor = 4
        self.depth = depth
        # nframe = 2
        ## not complete
        # self.nframe_in = 2
        # self.nframe_out = 15
        self.nframe = 15
        self.checkRod = np.empty((self.nGrid,self.nframe),dtype = '>U8')
        self.checkRod[:,:] = "--------"
        self.color_df = setColorShape()
        
        print("[INFO] starting video file thread...")
        self.w_original = 0
        self.h_original = 0

        self.cap = self.playMode(playmode,videofile)
        self.totalFrame = self.cap.getTotalFrame()

        self.w = 0
        self.h = 0
        self.grid = 0
        
        self.sd = ShapeDetector()
        self.k = 0
        
        self.image = self.readImage()
        self.overlay = self.image.copy()
        self.handPro = handDetection()
        cv2.imshow("Color Tracking",self.image)
        # cv2.setMouseCallback("Color Tracking", self.mouse_drawing)
        cv2.waitKey(1)
        self.margin_x = 45
        self.margin_y = 30
        self.timestamps = []
        self.checkcond = False
        self.saveDF = pd.DataFrame(columns=['code','time','actiontime','action','blockpos','blockdepth','rodlength'])
        self.saveProgress = pd.DataFrame(columns=['timestamp','progress','timefromstart'])

    def cheatingFun(self):
        # cheating
        self.counts = 8
        self.circles = np.array([ (242,  150),(1193,  163),(1171,  752),( 229,  719),( 362,  249),(1069,  262),(1050,  684),( 352,  670)], dtype = "float32")
        self.grid = self.createGrid()
        print(self.grid)
        if self.playmode == "Analysis":
            self.timestamps = self.cap.videoTime()

        self.warpFunction(self.circles[0:4])
        self.runImage()
        
    def playMode(self,playmode,videofile):
        self.playmode = playmode
        cap = FileVideoStream(videofile).start()
        width,height =cap.videoSize()
        
        print((width,height))
        self.w_original = width
        self.h_original = height
        
        return(cap)
    
    def readImage(self):
        # if self.playmode=="Analysis":
        image = self.cap.read()
        # else:
        #     if self.k == 0:
        #         for i in range(self.nframe):
        #             ret,image = self.cap.read()
        #     else:
        #         ret,image = self.cap.read()            
            
        #     self.out.write(image)
        return(image)
            
    def updateImage(self):
        if self.playmode=="Analysis":
            return(self.cap.more())
        else:
            return(True)
        
    def warpFunction(self,pts):
        warped = four_point_transform(self.image, pts)
    
        self.h, self.w, _ = warped.shape
        return(warped)

    def mouse_drawing(self,event, x, y, flags, params):
        if event == cv2.EVENT_LBUTTONDOWN:
            print("Left click")
            self.circles.append((x, y))
            print(x,y)
            self.counts += 1
            cv2.circle(self.image, (x,y), 10, (0, 0, 0), -1)
            cv2.imshow("Color Tracking",self.image)
            if self.counts >= 8:
                if self.playmode == "Analysis":
                    self.timestamps = self.cap.videoTime()
                #print(timestamps)
                self.circles = np.array(self.circles, dtype = "float32")
                print(self.circles)
                self.grid = self.createGrid()
                print(self.grid)
                self.warpFunction(self.circles[0:4])
                self.runImage()

    # call check hand detection contour in this function
    def updateGrid(self,p):
        for i in range(self.grid.shape[0]):
            if i in p:
                # can detect color
                if (not self.grid.exist[i]):
                    self.grid.loc[i,"count_1"] += 1
                    print('rod-in')
                    print(self.grid.loc[i,"count_1"])
                    if self.grid.loc[i,"count_1"] > self.nframe:
                        col, shape_code = self.checkRod_result[i].split("-")
                        self.grid.loc[i, "length_rod"] = self.color_df[(self.color_df.shape_1==int(shape_code))& 
                                 (self.color_df.color == col)].length.values[0]
                        self.grid.loc[i,"exist"] = True
                        self.grid.loc[i,"count_1"] = 0
                        now = datetime.datetime.now()
                        now.strftime("%Y-%m-%d %H:%M")
                        self.saveDF.loc[self.saveDF.shape[0]] = [self.name,now,self.timestamps[self.k-self.nframe],"rod-in",
                                        i,self.grid.depth_block[i],self.grid.length_rod[i]]
                elif (self.grid.exist[i]):
                    self.grid.loc[i,"count_1"] =0
            else:
                # cannot detect color
                if(self.grid.exist[i]):
                    self.grid.loc[i,"count_1"] += 1
                    chkhand = self.handPro.checkHand(self.overlay,self.grid.left_x[i],self.grid.left_y[i],self.grid.right_x[i],self.grid.right_y[i],self.grid.size_px[i])
                    print(chkhand)
                    print(self.grid.loc[i,"count_1"])
                    # true = hand blocks color
                    if self.grid.loc[i,"count_1"] > self.nframe and (not chkhand):
                        self.grid.loc[i,"exist"] = False
                        self.grid.loc[i,"count_1"] = 0
                        now = datetime.datetime.now()
                        now.strftime("%Y-%m-%d %H:%M")
                        self.saveDF.loc[self.saveDF.shape[0]] = [self.name,now,self.timestamps[self.k-self.nframe],"rod-out",i,self.grid.depth_block[i],self.grid.length_rod[i]]
                        self.grid.loc[i, "length_rod"] = 0
                else:
                    self.grid.loc[i,"count_1"] = 0
                    # if self.grid.exist == false, and no color is detected in grid
                    # if self.grid.loc[i,"count_1"] > 0:
                    #     self.grid.loc[i,"count_1"] += 1 
                    #     print("check")
                    # self.grid.loc[i,"count_1"] = 0

        return(self.grid)

    def updateRod(self,arr,col,shape_code,pos_grid):
        arr1 = np.roll(arr, -1, axis=1)
        last_col = arr.shape[1]-1
        dum = ["{}-{:1}".format(a_, b_) for a_, b_ in zip(col, shape_code)]

        for i in range(arr1.shape[0]):
            if i in pos_grid:
                #print(i)
                idx = pos_grid.index(i)
                arr1[i][last_col] = dum[idx]
                # print(arr1)
            else:
                arr1[i][last_col] = "--------"
        return(arr1)
    

    def createGrid(self):
        circles1 = self.circles[0:4]
        circles2 = self.circles[4:8]
        margin = np.array(np.absolute(circles1 - circles2),dtype=int)
        sizebox = np.array((circles2[2] - circles2[0])/[5,3],dtype=int)
        left_y = np.array((0,margin[0,1]+sizebox[1],margin[0,1]+2*sizebox[1]))
        left_y = np.repeat(left_y,5)
        left_x = np.array((0,margin[0,0]+sizebox[0],margin[0,0]+2*sizebox[0],margin[0,0]+3*sizebox[0],margin[0,0]+4*sizebox[0]))
        left_x = np.tile(left_x,3)
    
        #right
        right_y = np.array((margin[0,1]+sizebox[1],margin[0,1]+2*sizebox[1],margin[0,1]+margin[3,1]+3*sizebox[1]))
        right_y = np.repeat(right_y,5)
        right_x = np.array((margin[0,0]+sizebox[0],margin[0,0]+2*sizebox[0],margin[0,0]+3*sizebox[0],margin[0,0]+4*sizebox[0],margin[0,0]+margin[2,0]+5*sizebox[0]))
        right_x = np.tile(right_x,3)
        sizepx = np.absolute(left_x-right_x) * np.absolute(left_y-right_y)
        grid = pd.DataFrame(data={"left_x":left_x,"left_y":left_y,"right_x":right_x,"right_y":right_y,
                                       "depth_block":self.depth,"exist":False,"count_1":0,"length_rod":0, "size_px": sizepx})
        return(grid)

    def checkGrid(self,grid_info,m_x,m_y, x,y,radius):
        mx1 = np.tile(np.repeat(np.array([-m_x,0],dtype=int),[2,3]),3)
        mx2 = np.tile(np.repeat(np.array([0,m_x],dtype=int),[3,2]),3)
        my1 = np.tile(np.repeat(np.array([-m_y,0],dtype=int),[3,2]),3)
        pos = (grid_info.left_x + mx1 < x-radius) & (x+radius < grid_info.right_x+mx2) & (grid_info.left_y + my1 < y-radius) & (y+radius< grid_info.right_y)
        ##return only true, true = circle in that grid
        return(grid_info[pos[:]])

    def runImage(self):
        
        while (self.updateImage() and self.checkcond == False):
            if self.counts>=8:
                print(self.k)
                self.k += 1
                if self.playmode != "Analysis":
                    self.timestamps.append(time.time()-self.start_time)
                
                self.image = self.readImage()
                ### update: do a hand detection before crop and save it to new self.overlay
                overlay = self.handPro.detect(self.image,self.w_original,self.h_original)
                self.overlay = four_point_transform(overlay, self.circles[0:4])
                self.image = self.warpFunction(self.circles[0:4])
                
            
                hsv=cv2.cvtColor(self.image,cv2.COLOR_BGR2HSV)
            
                
        #        definig the ranges of color
        #       for red color, we have to include orange color as well.
                kernal = np.ones((5 ,5), "uint8")
                color_set = np.empty((4, int(self.h),int(self.w)),"uint8")
                for i in range(4):
                    lower=np.array(self.color_df.color_low[i],np.uint8)
                    upper=np.array(self.color_df.color_up[i],np.uint8)
                    dum = cv2.inRange(hsv, lower, upper)
                    
                    if i ==0:
                        lower1 = np.array([170,120,100],np.uint8)
                        upper1 = np.array([180,255,255],np.uint8)
                        dum1 = cv2.inRange(hsv,lower1,upper1)
                        dum = dum+dum1
                        
                    dum = cv2.dilate(dum, kernal)
                    color_set[i,:,:] = dum
                
                #recode infomation for updateGrid
                col = []
                shape_code = []
                pos_grid = []
                
                for i in range(4):
                    contours,hierarchy=cv2.findContours(color_set[i,:,:],cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        #            if len(contours) == 0:
        #                isRodGrid[i] = -1
                    for pic, contour in enumerate(contours):
                        (x,y),radius = cv2.minEnclosingCircle(contour)
                        p = self.checkGrid(self.grid,self.margin_x,self.margin_y,x,y,radius)
                        if(not(p.empty) and radius > 30):
                            center = (int(x),int(y))
                            radius = int(radius)
                            num,shape = self.sd.detect(contour)
            #                    print(num)
                            idx = i + self.ncolor*int(num)
                            self.image = cv2.circle(self.image,center,radius,self.color_df.col_code[idx],2)
                            cv2.putText(self.image,self.color_df.color[idx]+" color",(int(x),int(y)),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, self.color_df.col_code[idx])
                            cv2.putText(self.image, shape, (int(x),int(y)+20), cv2.FONT_HERSHEY_SIMPLEX,
                                        0.7, (255, 255, 255), 2)
                            
                            col.append(self.color_df.color[idx])
                            shape_code.append(num)
                            pos_grid.append(p.index.values[0])
                
                self.checkRod = self.updateRod(self.checkRod,col,shape_code,pos_grid)
                self.checkRod_result = np.apply_along_axis(chooseMax,1,self.checkRod)
                # print(self.checkRod_result)
                self.grid = self.updateGrid(pos_grid)
                
                self.updateRect(pos_grid)
                
                for i in range(self.nGrid):
                    self.image = cv2.rectangle(self.image,(self.grid.left_x[i],self.grid.left_y[i]),
                                             (self.grid.right_x[i],self.grid.right_y[i]),(0,0,0),3)
         
        #        resize = cv2.resize(img,(new_w, new_h))
                cv2.imshow("Color Tracking",self.image)
                # cv2.imshow("overlay",self.overlay)
                cv2.waitKey(1)
                
                #self.window.mainloop()
                self.window.update()
            
            signal.signal(signal.SIGINT, self.signal_handler)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
        
        if self.playmode == "Analysis":
            self.cap.stop()
        else:
            self.cap.release()
            self.out.release()
            
        cv2.destroyAllWindows()
        self.saveDF.to_csv(self.outputfile+".csv",index=False)
        self.saveProgress.to_csv(self.outputfile+"-time"+".csv",index=False)

        
    
    def updateRect(self,pos_grid):
        nrow,ncol = self.grid.shape
        for i in range(nrow):
            if self.grid.exist[i]:
                self.rect[i].change_fill()  
            else:
                self.rect[i].change_nofill()

        # txt = "Time: "+ str(int(self.timestamps[self.k]/1000))+" seconds, Analysis: "+ str(self.k/self.totalFrame *100) +" %"
        percent = self.k/self.totalFrame *100
        txt = "Time: {:0.2f} seconds,  Analysis: {:0.2f} %".format(self.timestamps[self.k]/1000,percent)
        self.timelbl.configure(text = txt)
        now = time.time()
        
        self.saveProgress.loc[self.saveProgress.shape[0]] = [now,percent,now - self.timestart]
        
        #"Equal-all","Equal-row","Equal-column"
        if self.cond == "Equal-all" and self.grid.exist.all() and (not self.checkcond):
            print(np.array(self.grid.depth_block,dtype=int))
            d = np.array(self.grid.depth_block,dtype=int) - np.array(self.grid.length_rod,dtype=int)
            k = (d==np.repeat(d[0],nrow))
            print(k)
            if k.all():
                messagebox.showinfo("Tangible game","The lengths are equal.")
                self.checkcond = True
                print(time.time()-self.timestart)
                
        elif self.cond == "Equal-row" and self.grid.exist.all() and (not self.checkcond):
            d = self.grid.depth_block - self.grid.length_rod
            k = (d== np.repeat(np.array((d[0],d[5],d[10])),5))
            if k.all():
                messagebox.showinfo("Tangible game","The lengths of each row are equal.")
                self.checkcond = True
                
        elif self.cond == "Equal-column" and self.grid.exist.all() and (not self.checkcond):
            d = self.grid.depth_block - self.grid.length_rod
            k = (d== np.tile(d[0:5],5))
            if k.all():
                messagebox.showinfo("Tangible game","The lengths of each column are equal.")
                self.checkcond = True
        
            
    def signal_handler(self,sig, frame):
        print('Stop the game!')
        self.stopImage()
        
    def stopImage(self):
        self.saveDF.to_csv(self.outputfile+".csv",index=False)
        self.saveProgress.to_csv(self.outputfile+"-time"+".csv",index=False)

        if self.playmode != "Analysis":
            self.out.release()
            self.cap.release()
        else:
            self.cap.stop()
            self.handPro.closeHand()
        cv2.destroyAllWindows()
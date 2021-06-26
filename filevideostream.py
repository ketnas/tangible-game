#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 15 21:58:51 2019

@author: Kejkaew
"""

from threading import Thread
from queue import Queue
import cv2

class FileVideoStream:
    def __init__(self, path, queueSize=128):
		# initialize the file video stream along with the boolean
		# used to indicate if the thread should be stopped or not
        self.stream = cv2.VideoCapture(path)
        self.stopped = False
        
        self.timestamps = [self.stream.get(cv2.CAP_PROP_POS_MSEC)]
 
		# initialize the queue used to store frames read from
		# the video file
        self.Q = Queue(maxsize=queueSize)
    
    def start(self):
		# start a thread to read frames from the file video stream
        t = Thread(target=self.update, args=())
        t.daemon = True
        t.start()
        return self
    
    def update(self):
		# keep looping infinitely
        while True:
			# if the thread indicator variable is set, stop the
			# thread
            if self.stopped:
                return
 
			# otherwise, ensure the queue has room in it
            if not self.Q.full():
				# read the next frame from the file
                (grabbed, frame) = self.stream.read()
 
				# if the `grabbed` boolean is `False`, then we have
				# reached the end of the video file
                if not grabbed:
                    self.stop()
                    return
                else:
                    self.timestamps.append(self.stream.get(cv2.CAP_PROP_POS_MSEC))
 
				# add the frame to the queue
                self.Q.put(frame)
                
    def read(self):
		# return next frame in the queue
        return self.Q.get()
    
    def more(self):
		# return True if there are still frames in the queue
        return self.Q.qsize() > 0
    
    def stop(self):
		# indicate that the thread should be stopped
        self.stopped = True
    
    def videoSize(self):
        return (self.stream.get(3),self.stream.get(4))

    def getTotalFrame(self):
        frame_count = int(self.stream.get(cv2.CAP_PROP_FRAME_COUNT))
        return frame_count
    
    def getFps(self):
        fps = self.stream.get(cv2.CAP_PROP_FPS)
        return (fps)

    def videoTime(self):
        return(self.timestamps)
        
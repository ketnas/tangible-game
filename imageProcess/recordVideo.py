import cv2
import signal


class realTime:
    def __init__(self,name,outputfile,window):
        self.outputfile = outputfile
        self.window = window

    def startRecord(self):
        self.cap = cv2.VideoCapture(0)
        width,height = (self.cap.get(3),self.cap.get(4))
        print((width,height))
        # self.start_time = time.time()
        self.out = cv2.VideoWriter(self.outputfile+".avi",cv2.VideoWriter_fourcc('M','J','P','G'), 10, (int(width),int(height)))
        self.recordVideo()

    def recordVideo(self):
        while (True):
            ret,self.image = self.cap.read()            
            cv2.imshow("Color Tracking",self.image)
            cv2.waitKey(1)
            self.out.write(self.image)
            self.window.update()
            signal.signal(signal.SIGINT, self.signal_handler)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cap.release()
        self.out.release()
            
        cv2.destroyAllWindows()

    def signal_handler(self,sig, frame):
        print('Stop the game!')
        self.stopImage()

    def stopImage(self):
        self.out.release()
        self.cap.release()

        cv2.destroyAllWindows()
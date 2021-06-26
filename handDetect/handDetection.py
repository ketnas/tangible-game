import cv2
import mediapipe as mp
import numpy as np

def scale_contour(cnt, scale):
    M = cv2.moments(cnt)
    cx = int(M['m10']/M['m00'])
    cy = int(M['m01']/M['m00'])

    cnt_norm = cnt - [cx, cy]
    cnt_scaled = cnt_norm * scale
    cnt_scaled = cnt_scaled + [cx, cy]
    cnt_scaled = cnt_scaled.astype(np.int32)

    return cnt_scaled

class handDetection:
    def __init__(self):
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)

    def detect(self, image1, image_width,image_height):
        image = image1.copy()
        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = self.hands.process(image)

        # Draw the hand annotations on the image.
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        overlay1 = image.copy()
        overlay2 = image.copy()
        self.output = image.copy()
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks: 
                self.mp_drawing.draw_landmarks(overlay1, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
            
            a = np.array([[[hand_landmarks.landmark[0].x*image_width,hand_landmarks.landmark[0].y*image_height]]])
            for i in [1,2,3,4,8,12,16,20,19,18,17]:
                b = np.array([[[hand_landmarks.landmark[i].x*image_width,hand_landmarks.landmark[i].y*image_height]]])
                a = np.concatenate((a,b),axis=0)
            
            a = a.astype('int32')
            overlay1 = cv2.drawContours(overlay1,[a],-1,(0,0,0),thickness=-1)
            s1 = np.column_stack(np.where(np.all(overlay1 == [0,0,0],axis=-1)))

            a2 = np.array([[[hand_landmarks.landmark[0].x*image_width,hand_landmarks.landmark[0].y*image_height]]])
            for i in [1,2,3,4,6,10,14,18,17]:
                b = np.array([[[hand_landmarks.landmark[i].x*image_width,hand_landmarks.landmark[i].y*image_height]]])
                a2 = np.concatenate((a2,b),axis=0)
            a2 = a2.astype('int32')
            overlay2 = cv2.drawContours(overlay2,[a2],-1,(0,0,0),thickness=-1)
            s2 = np.column_stack(np.where(np.all(overlay2 == [0,0,0],axis=-1)))

            
            if (s1.shape[0] > s2.shape[0]):
                # self.output = overlay1
                a3 = a.copy()
            else:
                # self.output = overlay2
                a3 = a2.copy()
            
            ## try to detect arm
            #  find centriod of all points
            a = np.array([[hand_landmarks.landmark[0].x*image_width,hand_landmarks.landmark[0].y*image_height]])
            for i in range(1,21):
                b = np.array([[hand_landmarks.landmark[i].x*image_width,hand_landmarks.landmark[i].y*image_height]])
                a = np.concatenate((a,b),axis=0)
            
            a = a.astype('int32')
            center = np.mean(a,axis = 0)
            
        #    find wrist
            a = np.array([[[hand_landmarks.landmark[0].x*image_width,hand_landmarks.landmark[0].y*image_height]]])
            for i in [1,17]:
                b = np.array([[[hand_landmarks.landmark[i].x*image_width,hand_landmarks.landmark[i].y*image_height]]])
                a = np.concatenate((a,b),axis=0)

            a = a.astype('int32')
        
        # create vectors and find orthagonal vectors
            k1 = np.array([[[0,0]]])
            for i in range(1,3):
                d = a[0] - a[i]
                d_orth1 = np.array([-d[0][1],d[0][0]])
                d_orth2 = np.array([d[0][1],-d[0][0]])
                d_coor1 = np.array([a[0] + d_orth1])
                d_coor2 = np.array([a[0] + d_orth2])
                k1 = np.concatenate((k1,d_coor1,d_coor2),axis=0)

            k1 = np.delete(k1,0,0)
            dist = np.linalg.norm(k1-center,axis = -1).flatten()
            pos = np.argsort(dist)[2:4]
            k1 = k1[pos]
            a5 = a
            # new_a1 = np.concatenate(([a5[0]],k1),axis=0)
            a = k1.reshape(2,2)
            # compute linear regression of arms 
            slope = (a[0][0] - a[1][0])/ (a[0][1] - a[1][1])
            m1 = m2 = - slope
            c1 = a[0][1] - m1*a[0][0]
            c2 = a[1][1] - m2*a[1][0]
            if abs(slope) < 100:
                finger_h = int(hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP].y*image_height)
                
                if  finger_h < a[0][1] or finger_h < a[1][1]:
                    print("y = heigth")
                    x1 = (image_height - c1) / m1
                    x2 = (image_height - c2) / m2
                    new_a2 = np.concatenate(([a5[0]], [k1[0]], [[[x1,image_height]]],[[[x2,image_height]]],[k1[1]]),axis=0)
                else:
                    print("y = 0")
                    x1 = (0 - c1) / m1
                    x2 = (0 - c2) / m2
                    new_a2 = np.concatenate(([a5[0]], [k1[0]], [[[x1,0]]],[[[x2,0]]],[k1[1]]),axis=0)
            else:
                finger_w = int(hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP].x*image_width)
                if finger_w < a[0][0] or finger_w < a[1][0]:
                    print("x = width")
                    y1 = image_width*m1 + c1
                    y2 = image_width*m2 + c2
                    new_a2 = np.concatenate(([a5[0]], [k1[0]], [[[image_width,y1]]],[[[image_width,y2]]],[k1[1]]),axis=0)
                else:
                    print("x = 0")
                    y1 =  c1
                    y2 =  c2
                    new_a2 = np.concatenate(([a5[0]], [k1[0]], [[[0,y1]]],[[[0,y2]]],[k1[1]]),axis=0)
            
        #    this is the wrist and arm area
            new_a2 = new_a2.astype('int32')
            
            new_a2 = np.delete(new_a2,0,0)
            new_a3 = np.flip(new_a2, 0)
            a3 = np.delete(a3,0,0)
            new_a4 = np.concatenate((a3,new_a3),axis = 0)
            # scale the contour so it will increase accuracy of hand detection
            new_a4 = scale_contour(new_a4,1.3)
            overlay1 = image.copy()
            self.output = cv2.drawContours(overlay1,[new_a4],-1,(0,0,0),thickness=-1)

        self.output = cv2.flip(self.output, 1)
        return(self.output)

    def checkHand(self,image_wrap,x1,y1,x2,y2,gridsize):
        print((x1,y1),(x2,y2))
        s1 = np.column_stack(np.where(np.all(image_wrap == [0,0,0],axis=-1)))
        blkarea = sum(np.all(s1 <= [y2,x2], axis=-1)& np.all(s1 >= [y1,x1], axis = -1))
        # true = hand block color
        print(s1.shape)
        print(blkarea)
        print(gridsize*0.1)
        return(blkarea > gridsize*0.1)

    def closeHand(self):
        self.hands.close()

##testing
# if __name__ == '__main__':
#     videofile = "t2.avi"
#     cap = cv2.VideoCapture(videofile)
#     image_height, image_width = (cap.get(4),cap.get(3))
#     print((image_height, image_width))
#     #image = cap.read()
#     handPro = handDetection()
#     #cv2.imshow('MediaPipe Hands', image)
#     #cv2.waitKey(5)
    
#     while (cap.isOpened()):
#         success,image = cap.read()
#         out = handPro.detect(image,image_width,image_height)
#         cv2.imshow('MediaPipe Hands', out)
#         if cv2.waitKey(5) & 0xFF == 27:
#             break
        
#     handPro.closeHand()
#     cap.release()
#     cv2.destroyAllWindows()
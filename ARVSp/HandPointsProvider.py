import cv2
import mediapipe as mp
import os
import time
from google.protobuf.json_format import MessageToDict
from GeneralFunctions import *

class HandPointsProvider:
    def __init__(self,cap):
        self.cap = cap
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands()

    def GetHandPoints(self):
        #cap = cv2.VideoCapture(0)
        #cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  #设置宽度
        #cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  #设置高度

        success, img = self.cap.read()
        img=cv2.flip(img, 1)
        #转换一下后RGB错误，但识别效率提升
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)//cv2.COLOR_BGR2RGB
        #timePoint1=time.perf_counter()
        results = self.hands.process(imgRGB)
        #timePoint2=time.perf_counter()
        #print ((timePoint2-timePoint1)*1000)
        #img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)//cv2.COLOR_BGR2RGB
        listPoints=[]
        if results.multi_hand_landmarks:
            for handId , handObj in enumerate(results.multi_hand_landmarks):
                ## 左右手
                #handedness_dict = MessageToDict(results.multi_handedness[handId])
                #res_handed = int(handedness_dict['classification'][0]['index'])

                for id, point in enumerate(handObj.landmark):
                    h, w, c = img.shape
                    cx, cy, cz= int(point.x * w), int(point.y * h),int(point.z * w)
                    listPoints.append(Point3D(cx, cy, cz))

        return listPoints,img

if __name__=="__main__":
    cap = cv2.VideoCapture(0)

    pointsAsker=HandPointsProvider(cap)

    while True:
        listPoints, img = pointsAsker.GetHandPoints()
        for eachPoint in listPoints:
            cx,cy,cz=eachPoint.X,eachPoint.Y,eachPoint.Z
            radius = int(cz * 0.1) + 1
            if radius > 0:
                cv2.circle(img, (cx, cy), radius, (0, 255, 255), cv2.FILLED)  # 圆
            else:
                radius = -radius
                cv2.circle(img, (cx, cy), radius, (255, 0, 0), cv2.FILLED)  # 圆

        cv2.imshow("Image", img)

        if ord('q') == cv2.waitKey(1):
            break
        if 27 == cv2.waitKey(1):
            break


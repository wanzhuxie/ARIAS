# !/usr/bin/python
# -*- coding: utf-8 -*-

# -------------------------------------------
#
# -------------------------------------------

from OpenGL.GL import *
from OpenGL.GLUT import *
import cv2
import sys
import time
from OpenGL.GLU import *
from PIL import Image
from HandPointsProvider import *
from GestureRecognizer import *
import threading

class ARVSMain:
    def __init__(self,
        width=640,
        height=480):
        self.InitGL(width, height)

        #rotate around XYZ axes
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0

        self.cap1 = cv2.VideoCapture("video1.mp4")
        self.cap2 = cv2.VideoCapture("video2.mp4")
        self.cap3 = cv2.VideoCapture("video3.mp4")
        self.cap4 = cv2.VideoCapture("video4.mp4")
        self.cap5 = cv2.VideoCapture("video5.mp4")
        self.cap6 = cv2.VideoCapture("video6.mp4")
        self.frameCount1=self.cap1.get(cv2.CAP_PROP_FRAME_COUNT)
        self.frameCount2=self.cap2.get(cv2.CAP_PROP_FRAME_COUNT)
        self.frameCount3=self.cap3.get(cv2.CAP_PROP_FRAME_COUNT)
        self.frameCount4=self.cap4.get(cv2.CAP_PROP_FRAME_COUNT)
        self.frameCount5=self.cap5.get(cv2.CAP_PROP_FRAME_COUNT)
        self.frameCount6=self.cap6.get(cv2.CAP_PROP_FRAME_COUNT)

        self.cap0 = cv2.VideoCapture(0)
        self.handPointsAsker = HandPointsProvider(self.cap0)
        self.listHandPoints=[]
        self.InitCap0,self.img0=self.cap0.read()

    # InitGL
    def InitGL(self, width, height):
        glutInit()
        glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
        glutInitWindowSize(width, height)
        self.window = glutCreateWindow("ARVS")
        glutDisplayFunc(self.Draw)
        glutIdleFunc(self.Draw)

        glEnable(GL_TEXTURE_2D)
        glClearColor(1.0, 1.0, 1.0, 0.0)
        glClearDepth(1.0)
        glDepthFunc(GL_LESS)
        glShadeModel(GL_SMOOTH)

        # Back culling, blanking [the effect is not obvious]
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        glEnable(GL_POINT_SMOOTH)
        glEnable(GL_LINE_SMOOTH)
        glEnable(GL_POLYGON_SMOOTH)
        glMatrixMode(GL_PROJECTION)
        glHint(GL_POINT_SMOOTH_HINT, GL_NICEST)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        glHint(GL_POLYGON_SMOOTH_HINT, GL_FASTEST)
        glLoadIdentity()
        gluPerspective(45.0, float(width) / float(height), 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)

    #draw_background
    def draw_background(self,img):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        # Setting background image project_matrix and model_matrix.
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(33.7, 1.3, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        bg_img = cv2.flip(img, 0)
        bg_img = Image.fromarray(bg_img)
        ix = bg_img.size[0]
        iy = bg_img.size[1]
        bg_img = bg_img.tobytes("raw", "BGRX", 0, -1)


        # Create background texture
        texid = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texid)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexImage2D(GL_TEXTURE_2D, 0, 3, ix, iy, 0, GL_RGBA, GL_UNSIGNED_BYTE, bg_img)

        glTranslatef(0.0, 0.0, -10.0)
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 1.0)
        glVertex3f(-4.0, -3.0, 0.0)
        glTexCoord2f(1.0, 1.0)
        glVertex3f(4.0, -3.0, 0.0)
        glTexCoord2f(1.0, 0.0)
        glVertex3f(4.0, 3.0, 0.0)
        glTexCoord2f(0.0, 0.0)
        glVertex3f(-4.0, 3.0, 0.0)
        glEnd()

    #call this mathed through multi threat
    def GetHandPoints(self):
        while True:
            #timePoint1=time.perf_counter()
            self.listHandPoints, self.img0=self.handPointsAsker.GetHandPoints()
            #time.sleep(0.05)
            for eachPoint in self.listHandPoints:
                cx, cy, cz = eachPoint.X, eachPoint.Y, eachPoint.Z
                radius = int(cz * 0.1) + 1
                if radius > 0:
                    cv2.circle(self.img0, (cx, cy), radius, (0, 255, 255), cv2.FILLED)  # 圆
                else:
                    radius = -radius
                    cv2.circle(self.img0, (cx, cy), radius, (255, 0, 0), cv2.FILLED)  # 圆

            #cv2.imshow("Background", self.img0)
            cv2.waitKey(20)
            #timePoint2=time.perf_counter()
            #print ("GetHandPoints:", "%.2f" % ((timePoint2-timePoint1)*1000), "ms")

    # draw main
    def Draw2(self):
        timePoint1=time.perf_counter()
        #Get hand points
        listPoints,img = self.handPointsAsker.GetHandPoints()

        ##do not work ??????
        self.draw_background(img)

        self.LoadTexture()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glLoadIdentity()

        #Translate along z-axis
        glTranslate(0.0, 0.0, -5.0)

        #Rotate around the x, y, z axes respectively
        glRotatef(self.x, 1.0, 0.0, 0.0)
        glRotatef(self.y, 0.0, 1.0, 0.0)
        glRotatef(self.z, 0.0, 0.0, 1.0)

        timePoint3=time.perf_counter()
        self.DrawBox()
        timePoint4=time.perf_counter()
        #print ((timePoint4-timePoint3)*1000)

        #Refresh screen
        glutSwapBuffers()

        #get gesture #get state
        gestureRecgonizer = GestureRecognizer(listPoints)
        fingerState=""
        fingerState=gestureRecgonizer.GetFingerState()
        print (fingerState)

        if fingerState == "00000":
            self.x += 0
            self.y += 0
            self.z += 0
        elif fingerState == "01000":
            self.x += 0.2
            self.y += 0.4
            self.z += 0.6
        elif fingerState == "01100":
            self.x += 0.4
            self.y += 0.8
            self.z += 1.2
        elif fingerState == "01110":
            self.x += 1
            self.y += 2
            self.z += 3
        else:
            self.x += 0.1
            self.y += 0.2
            self.z += 0.1

        timePoint2=time.perf_counter()
        print ("LoadTexture:", "%.2f" % ((timePoint2-timePoint1)*1000), "ms")
    #draw main(using GetHandPoints through multi-threat)
    def Draw(self):
        timePoint1=time.perf_counter()

        #background
        if self.InitCap0:
            self.draw_background(self.img0)

        ##15-19ms
        self.LoadTexture()

        glLoadIdentity()

        #Translate along z-axis
        glTranslate(0.0, 0.0, -5.0)

        #Rotate around the x, y, z axes respectively
        glRotatef(self.x, 1.0, 0.0, 0.0)
        glRotatef(self.y, 0.0, 1.0, 0.0)
        glRotatef(self.z, 0.0, 0.0, 1.0)

        self.DrawBox()

        #Refresh screen
        glutSwapBuffers()

        #====0.02-0.05ms====
        #get gesture #get state
        gestureRecgonizer = GestureRecognizer(self.listHandPoints)
        fingerState=gestureRecgonizer.GetFingerState()
        if fingerState!="":
            print (fingerState)
        #====0.02-0.05ms====

        if fingerState == "00000":
            self.x += 0
            self.y += 0
            self.z += 0
        elif fingerState == "01000":
            self.x += 0.2
            self.y += 0.4
            self.z += 0.6
        elif fingerState == "01100":
            self.x += 0.4
            self.y += 0.8
            self.z += 1.2
        elif fingerState == "01110":
            self.x += 1
            self.y += 2
            self.z += 3
        else:
            self.x += 0.0
            self.y += 0.0
            self.z += 0.0

        timePoint2=time.perf_counter()
        #print ("Draw:", "%.2f" % ((timePoint2-timePoint1)*1000), "ms")

    # Box 0.1-0.2ms
    def DrawBox(self):
        #face1
        glBindTexture(GL_TEXTURE_2D, 0)
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0)
        glVertex3f(-1.0, -1.0, 1.0)
        glTexCoord2f(1.0, 0.0)
        glVertex3f(1.0, -1.0, 1.0)
        glTexCoord2f(1.0, 1.0)
        glVertex3f(1.0, 1.0, 1.0)
        glTexCoord2f(0.0, 1.0)
        glVertex3f(-1.0, 1.0, 1.0)
        glEnd()

        #face2
        glBindTexture(GL_TEXTURE_2D, 1)
        glBegin(GL_QUADS)
        glTexCoord2f(1.0, 0.0)
        glVertex3f(-1.0, -1.0, -1.0)
        glTexCoord2f(1.0, 1.0)
        glVertex3f(-1.0, 1.0, -1.0)
        glTexCoord2f(0.0, 1.0)
        glVertex3f(1.0, 1.0, -1.0)
        glTexCoord2f(0.0, 0.0)
        glVertex3f(1.0, -1.0, -1.0)
        glEnd()

        #face3
        glBindTexture(GL_TEXTURE_2D, 2)
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 1.0)
        glVertex3f(-1.0, 1.0, -1.0)
        glTexCoord2f(0.0, 0.0)
        glVertex3f(-1.0, 1.0, 1.0)
        glTexCoord2f(1.0, 0.0)
        glVertex3f(1.0, 1.0, 1.0)
        glTexCoord2f(1.0, 1.0)
        glVertex3f(1.0, 1.0, -1.0)
        glEnd()

        #face4
        glBindTexture(GL_TEXTURE_2D, 3)
        glBegin(GL_QUADS)
        glTexCoord2f(1.0, 1.0)
        glVertex3f(-1.0, -1.0, -1.0)
        glTexCoord2f(0.0, 1.0)
        glVertex3f(1.0, -1.0, -1.0)
        glTexCoord2f(0.0, 0.0)
        glVertex3f(1.0, -1.0, 1.0)
        glTexCoord2f(1.0, 0.0)
        glVertex3f(-1.0, -1.0, 1.0)
        glEnd()

        #face5
        glBindTexture(GL_TEXTURE_2D, 4)
        glBegin(GL_QUADS)
        glTexCoord2f(1.0, 0.0)
        glVertex3f(1.0, -1.0, -1.0)
        glTexCoord2f(1.0, 1.0)
        glVertex3f(1.0, 1.0, -1.0)
        glTexCoord2f(0.0, 1.0)
        glVertex3f(1.0, 1.0, 1.0)
        glTexCoord2f(0.0, 0.0)
        glVertex3f(1.0, -1.0, 1.0)
        glEnd()

        #face6
        glBindTexture(GL_TEXTURE_2D, 5)
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0)
        glVertex3f(-1.0, -1.0, -1.0)
        glTexCoord2f(1.0, 0.0)
        glVertex3f(-1.0, -1.0, 1.0)
        glTexCoord2f(1.0, 1.0)
        glVertex3f(-1.0, 1.0, 1.0)
        glTexCoord2f(0.0, 1.0)
        glVertex3f(-1.0, 1.0, -1.0)
        glEnd()


    #LoadTexture 20-25ms [the Overall CPU occupancy is  65%]
    def LoadTexture(self):
        if self.cap1.get(cv2.CAP_PROP_POS_FRAMES) == self.frameCount1:    self.cap1.set(cv2.CAP_PROP_POS_FRAMES, 0)
        if self.cap2.get(cv2.CAP_PROP_POS_FRAMES) == self.frameCount2:    self.cap2.set(cv2.CAP_PROP_POS_FRAMES, 0)
        if self.cap3.get(cv2.CAP_PROP_POS_FRAMES) == self.frameCount3:    self.cap3.set(cv2.CAP_PROP_POS_FRAMES, 0)
        if self.cap4.get(cv2.CAP_PROP_POS_FRAMES) == self.frameCount4:    self.cap4.set(cv2.CAP_PROP_POS_FRAMES, 0)
        if self.cap5.get(cv2.CAP_PROP_POS_FRAMES) == self.frameCount5:    self.cap5.set(cv2.CAP_PROP_POS_FRAMES, 0)
        if self.cap6.get(cv2.CAP_PROP_POS_FRAMES) == self.frameCount6:    self.cap6.set(cv2.CAP_PROP_POS_FRAMES, 0)
        success1, img1 = self.cap1.read()
        success2, img2 = self.cap2.read()
        success3, img3 = self.cap3.read()
        success4, img4 = self.cap4.read()
        success5, img5 = self.cap5.read()
        success6, img6 = self.cap6.read()
        img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2RGBA)
        img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2RGBA)
        img3 = cv2.cvtColor(img3, cv2.COLOR_BGR2RGBA)
        img4 = cv2.cvtColor(img4, cv2.COLOR_BGR2RGBA)
        img5 = cv2.cvtColor(img5, cv2.COLOR_BGR2RGBA)
        img6 = cv2.cvtColor(img6, cv2.COLOR_BGR2RGBA)
        list_img=[img1,img2,img3,img4,img5,img6]
        for i in range(6):
            img = list_img[i]
            h1, w1, c1 = img.shape
            glGenTextures(2)
            glBindTexture(GL_TEXTURE_2D, i)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w1, h1, 0, GL_RGBA, GL_UNSIGNED_BYTE, img.data)
            glTexParameterf(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S, GL_CLAMP)
            glTexParameterf(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T, GL_CLAMP)
            glTexParameterf(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameterf(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T, GL_REPEAT)
            glTexParameterf(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER, GL_NEAREST)
            glTexParameterf(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER, GL_NEAREST)
            glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
    #LoadTexture(multi-threat) 15-19ms [the Overall CPU occupancy is 100%]
    def LoadTexture2(self):
        thread_list = []
        t1 = threading.Thread(target=self.CreateOneTexture,args=( 1, self.cap1, self.frameCount1))
        t2 = threading.Thread(target=self.CreateOneTexture,args=( 2, self.cap2, self.frameCount2))
        t3 = threading.Thread(target=self.CreateOneTexture,args=( 3, self.cap3, self.frameCount3))
        t4 = threading.Thread(target=self.CreateOneTexture,args=( 4, self.cap4, self.frameCount4))
        t5 = threading.Thread(target=self.CreateOneTexture,args=( 5, self.cap5, self.frameCount5))
        t6 = threading.Thread(target=self.CreateOneTexture,args=( 6, self.cap6, self.frameCount6))
        thread_list.append(t1)
        thread_list.append(t2)
        thread_list.append(t3)
        thread_list.append(t4)
        thread_list.append(t5)
        thread_list.append(t6)

        for t in thread_list:
            #t.setDaemon(True)  # daemon thread will not be interrupted by the main thread ends
            t.start()
        for t in thread_list:
            t.join() # the main thread wait all sub  threat completed

        listFrame=[]
        listFrame.append(self.img1)
        listFrame.append(self.img2)
        listFrame.append(self.img3)
        listFrame.append(self.img4)
        listFrame.append(self.img5)
        listFrame.append(self.img6)

        for i in range(6):
            h1, w1, c1 = listFrame[i].shape
            glGenTextures(2)
            glBindTexture(GL_TEXTURE_2D, i)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w1, h1, 0, GL_RGBA, GL_UNSIGNED_BYTE, listFrame[i].data)
            glTexParameterf(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S, GL_CLAMP)
            glTexParameterf(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T, GL_CLAMP)
            #glTexParameterf(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S, GL_REPEAT)
            #glTexParameterf(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T, GL_REPEAT)
            glTexParameterf(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER, GL_NEAREST)
            glTexParameterf(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER, GL_NEAREST)
            #glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
    #Use with LoadTexture(multi-threat)
    def CreateOneTexture(self,i,cap,frameCount):
        if cap.get(cv2.CAP_PROP_POS_FRAMES) == frameCount:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        success, img = cap.read()
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)
        if i == 1:
            self.img1=img
        elif i==2:
            self.img2=img
        elif i==3:
            self.img3=img
        elif i==4:
            self.img4=img
        elif i==5:
            self.img5=img
        elif i==6:
            self.img6=img

    #MainLoop
    def MainLoop(self):
        glutMainLoop()

if __name__ == '__main__':
    w = ARVSMain()
    t = threading.Thread(target=w.GetHandPoints)
    t.start()
    w.MainLoop()




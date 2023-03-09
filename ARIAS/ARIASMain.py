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
from MarkerRecognizer import *
import threading
import numpy as np
from FaceBlanking import *

class ARIASMain:
    def __init__(self):
        self.cap0 = cv2.VideoCapture(0)
        self.width, self.height = map(int, (self.cap0.get(3), self.cap0.get(4)))

        self.InitGL(self.width, self.height)
        listState=["Initial","FrontView","Move","Rotate","Zoom"]
        self.curState="Initial"
        self._bKeepState=False
        self._strLastFingerState=""

        #world corner coor of the marker
        self.worldMarkerCorner=np.array([[-0.5, -0.5, 0],[-0.5, 0.5, 0],[0.5, 0.5, 0],[0.5, -0.5, 0]],dtype = np.float64)
        self.mappingWidth=0.4
        #thinkpad camera
        self.camera_matrix = np.array([
            [621.6733	,0			,301.8697],
            [0			,596.7352 	,223.5491],
            [0			,0			,1       ]],dtype = np.float64)
        self.dist_coeff = np.array([-0.4172, -0.1135, -0.0010, -0.0061, 0.7764] , dtype = np.float64)

        #ConstructProjectionMatrix
        self.projectionMatrix=self.ConstructProjectionMatrix(self.camera_matrix,self.width, self.height,0.01,100)
        self.modelMatrix=None

        self.bCreatedArBox=False
        self.bAppearNewMarker=False

        #handPoints
        self.handPointsAsker = HandPointsProvider(self.cap0)
        self.listHandPoints=[]

        self.img0 = None
        #_,self.img0=self.cap0.read()

        #rotate around XYZ axes
        self._RotateX = 0.0
        self._RotateY = 0.0
        self._RotateZ = 0.0
        self._dMoveX =0
        self._dMoveY =0
        self._dZoom=10
        self.cap1 = cv2.VideoCapture("videos/video1.mp4")
        self.cap2 = cv2.VideoCapture("videos/video2.mp4")
        self.cap3 = cv2.VideoCapture("videos/video3.mp4")
        self.cap4 = cv2.VideoCapture("videos/video4.mp4")
        self.cap5 = cv2.VideoCapture("videos/video5.mp4")
        self.cap6 = cv2.VideoCapture("videos/video6.mp4")
        self.frameCount1=self.cap1.get(cv2.CAP_PROP_FRAME_COUNT)
        self.frameCount2=self.cap2.get(cv2.CAP_PROP_FRAME_COUNT)
        self.frameCount3=self.cap3.get(cv2.CAP_PROP_FRAME_COUNT)
        self.frameCount4=self.cap4.get(cv2.CAP_PROP_FRAME_COUNT)
        self.frameCount5=self.cap5.get(cv2.CAP_PROP_FRAME_COUNT)
        self.frameCount6=self.cap6.get(cv2.CAP_PROP_FRAME_COUNT)

        self.markerRecognizer=MarkerRecognizer()

        self.FaceBlankingBox =FaceBlankingBox()

        #Tips
        self.listMasks=[]
        self.listMasks.append(cv2.imread("Tips/mask1.jpg"));
        self.listMasks.append(cv2.imread("Tips/mask2.jpg"));
        self.listMasks.append(cv2.imread("Tips/mask3.jpg"));
        self.listMasks.append(cv2.imread("Tips/mask4.jpg"));
        self.listMasks.append(cv2.imread("Tips/mask5.jpg"));
        self.listMaskPos=[]
        self.TextTipHight = 15
        self.IconTipWidth =self.listMasks[0].shape[0]
        self.listMaskPos.append((0 * self.IconTipWidth + 5, self.height - self.IconTipWidth))
        self.listMaskPos.append((1 * self.IconTipWidth + 5, self.height - self.IconTipWidth))
        self.listMaskPos.append((2 * self.IconTipWidth + 5, self.height - self.IconTipWidth))
        self.listMaskPos.append((3 * self.IconTipWidth + 5, self.height - self.IconTipWidth))
        self.listMaskPos.append((4 * self.IconTipWidth + 5, self.height - self.IconTipWidth))
    # InitGL
    def InitGL(self, width, height):
        glutInit()
        glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
        glutInitWindowSize(width, height)
        self.window = glutCreateWindow("ARIAS")
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

    # operation tips
    def DrawOperationTips(self,img):
        iActiveIndex=0
        #text tips
        listActiveTextIndex=[]
        strTips="Current state: "
        if self.curState=="Initial":
            iActiveIndex=0
            strTips = strTips + "Initialization"
            if not self.bCreatedArBox:
                strTips = strTips + "\n  Show your QR code"
            else:
                strTips = strTips +"\n  Show your hand to [Fronting]"
        elif self.curState=="FrontView":
            iActiveIndex=1
            strTips = strTips + "Fronting"
            strTips = strTips +"\n  01000 : display video 1"
            strTips = strTips +"\n  01100 : display video 2"
            strTips = strTips +"\n  01110 : display video 3"
            strTips = strTips +"\n  01111 : display video 4"
            strTips = strTips +"\n  11111 : display video 5"
            strTips = strTips +"\n  10001 : display video 6"
            #active tips
            if self.strCurFingereState=="01000":
                listActiveTextIndex.append(1)
            elif self.strCurFingereState == "01100":
                listActiveTextIndex.append(2)
            elif self.strCurFingereState=="01110":
                listActiveTextIndex.append(3)
            elif self.strCurFingereState=="01111":
                listActiveTextIndex.append(4)
            elif self.strCurFingereState == "11111":
                listActiveTextIndex.append(5)
            elif self.strCurFingereState=="10001":
                listActiveTextIndex.append(6)
        elif self.curState=="Move":
            iActiveIndex =2
            strTips = strTips + "Translation"
            strTips = strTips +"\n  01000 : to left"
            strTips = strTips +"\n  01100 : to right"
            strTips = strTips +"\n  01110 : to up"
            strTips = strTips +"\n  01111 : to down"
            #active tips
            if self.strCurFingereState=="01000":
                listActiveTextIndex.append(1)
            elif self.strCurFingereState == "01100":
                listActiveTextIndex.append(2)
            elif self.strCurFingereState == "01110":
                listActiveTextIndex.append(3)
            elif self.strCurFingereState == "01111":
                listActiveTextIndex.append(4)
        elif self.curState == "Rotate":
            iActiveIndex =3
            strTips = strTips + "Rotation"
            strTips = strTips + "\n  01000 : on X axis"
            strTips = strTips + "\n  00100 : on Y axis"
            strTips = strTips + "\n  00010 : on Z axis"
            strTips = strTips + "\n  10000 : reverse rotation"
            #active tips
            if len(self.strCurFingereState)>=5:
                if self.strCurFingereState[1]=="1":
                    listActiveTextIndex.append(1)
                if self.strCurFingereState[2] == "1":
                    listActiveTextIndex.append(2)
                if self.strCurFingereState[3] == "1":
                    listActiveTextIndex.append(3)
                if self.strCurFingereState[0] == "1":
                    listActiveTextIndex.append(4)
        elif self.curState=="Zoom":
            iActiveIndex =4
            strTips = strTips + "Zooming"
            strTips = strTips +"\n  01000 : zooming in"
            strTips = strTips +"\n  11000 : zooming out"
            #active tips
            if self.strCurFingereState=="01000":
                listActiveTextIndex.append(1)
            elif self.strCurFingereState == "11000":
                listActiveTextIndex.append(2)
        #image tips
        AddMasks(img,self.listMasks,self.listMaskPos,iActiveIndex)
        #text tips
        y0=self.height-self.IconTipWidth
        for i, txt in enumerate(strTips.split("\n")):
            y=self.height-self.IconTipWidth-(i+1)*self.TextTipHight
            if i in listActiveTextIndex:
                cv2.putText(img,txt,(20,y),cv2.FONT_HERSHEY_TRIPLEX,0.5,(200,0,0),1,None,True)
            else:
                cv2.putText(img,txt,(20,y),cv2.FONT_HERSHEY_TRIPLEX,0.5,(100,100,0),1,None,True)

    #draw_background
    def draw_background(self,img):
        #img[:]=[255,255,255]
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        # Setting background image project_matrix and model_matrix.
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(33.7, 1.3, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        bg_img = cv2.flip(img, 0)
        #bg_img=img
        #operation tips
        self.DrawOperationTips(bg_img)

        bg_img = Image.fromarray(bg_img)
        ix = bg_img.size[0]
        iy = bg_img.size[1]
        bg_img = bg_img.tobytes("raw", "BGRX",0,-1)


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

    def ConstructProjectionMatrix(self, cameraMatrix, width, height, near_plane=0.01, far_plane=100.0):
        P = np.zeros(shape=(4, 4), dtype=np.float32)

        fx, fy = cameraMatrix[0, 0], cameraMatrix[1, 1]
        cx, cy = cameraMatrix[0, 2], cameraMatrix[1, 2]

        P[0, 0] = 2 * fx / width
        P[1, 1] = 2 * fy / height
        P[2, 0] = 1 - 2 * cx / width
        P[2, 1] = 2 * cy / height - 1
        P[2, 2] = -(far_plane + near_plane) / (far_plane - near_plane)
        P[2, 3] = -1.0
        P[3, 2] = - (2 * far_plane * near_plane) / (far_plane - near_plane)

        return P.flatten()
    def ConstructModelMatrix(self,rvec,tvec):
        R, _ = cv2.Rodrigues(rvec)

        Rx = np.array([
            [1, 0, 0],
            [0, -1, 0],
            [0, 0, -1]
        ])

        tvec = tvec.flatten().reshape((3, 1))

        transform_matrix = Rx @ np.hstack((R, tvec))
        M = np.eye(4)
        M[:3, :] = transform_matrix
        return M.T.flatten()

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

    #draw main(using GetHandPoints through multi-threat)
    def Draw(self):
        timePoint1=time.perf_counter()

        #not work...
        self.GestureControl()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        self.bAppearNewMarker=False
        #background
        listMarkers=[]
        if self.img0 is not None:
            self.draw_background(self.img0)

            #markerRecognizer1 = time.perf_counter()
            #3-4ms
            listMarkers=self.markerRecognizer.Recognize(self.img0)
            #markerRecognizer2=time.perf_counter()
            #print ("markerRecognizer:", "%.2f" % ((markerRecognizer2-markerRecognizer1)*1000), "ms")

        ##15-19ms
        self.LoadTexture()

        #glLoadIdentity()

        #Translate along z-axis
        #glTranslate(0.0, 0.0, -5.0)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glMultMatrixf(self.projectionMatrix)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        #glEnable(GL_DEPTH_TEST)
        #glShadeModel(GL_FLAT)

        for i in range (len(listMarkers)):
            eachMarker=np.array(listMarkers[i],dtype=np.float64)
            retval, rvec, tvec = cv2.solvePnP(self.worldMarkerCorner,eachMarker,self.camera_matrix,self.dist_coeff)
            self.modelMatrix=self.ConstructModelMatrix(rvec, tvec)
            glLoadMatrixf(self.modelMatrix)

            self.DrawBox()
            self.curState = "Initial"
            self.bAppearNewMarker = True
            self.bCreatedArBox=True

        glLoadIdentity()
        glTranslatef(self._dMoveX, self._dMoveY, self._dZoom)
        glRotatef(self._RotateZ, 0, 0, 1)
        glRotatef(self._RotateY, 0, 1, 0)
        glRotatef(self._RotateX, 1, 0, 0)

        #
        if self.bCreatedArBox and not self.bAppearNewMarker:
            if self.curState == "Initial":
                glMatrixMode(GL_PROJECTION)
                glLoadIdentity()
                glLoadMatrixf(self.projectionMatrix)

                glMatrixMode(GL_MODELVIEW)
                glLoadIdentity()
                #glEnable(GL_DEPTH_TEST)
                #glShadeModel(GL_SMOOTH)
                glLoadMatrixf(self.modelMatrix)
            self.DrawBox()

        #Refresh screen
        glutSwapBuffers()

        timePoint2=time.perf_counter()
        print ("draw:", "%.2f" % ((timePoint2-timePoint1)*1000), "ms")

    def GestureControl(self):
        # Rotate around the x, y, z axes respectively
        #glRotatef(self._RotateX, 1.0, 0.0, 0.0)
        #glRotatef(self._RotateY, 0.0, 1.0, 0.0)
        #glRotatef(self._RotateZ, 0.0, 0.0, 1.0)

        # ====0.02-0.05ms====
        # get gesture #get state
        gestureRecgonizer = GestureRecognizer(self.listHandPoints)
        self.strCurFingereState = gestureRecgonizer.GetFingerState()
        strCurFingereState=self.strCurFingereState
        if strCurFingereState == "":
            return
        print(strCurFingereState)
        # ====0.02-0.05ms====
        #state change
        if self.bCreatedArBox:
            if strCurFingereState=="00000" or strCurFingereState=="11111":
                if strCurFingereState=="11111" and self._strLastFingerState=="00000":
                    self._bKeepState=True
                    if self.curState=="Initial":
                        self.curState ="FrontView"
                        print("====Initial=FrontView====")
                    elif self.curState=="FrontView":
                        self.curState = "Move"
                        print("====FrontView=Move====")
                    elif self.curState=="Move":
                        self.curState = "Rotate"
                        print("====Move=Rotate====")
                    elif self.curState=="Rotate":
                        self.curState="Zoom"
                        print("====Rotate=Zoom====")
                    elif self.curState=="Zoom":
                        self.curState = "FrontView"
                        print("====Zoom=FrontView====")
                elif strCurFingereState=="11111" and self.curState=="FrontView":
                    if not self._bKeepState:
                        self._RotateX=90
                        self._RotateY=0
                        self._RotateZ=0
                self._strLastFingerState=strCurFingereState
            else:
                self._bKeepState = False
                if self.curState == "Initial" and self.bCreatedArBox:
                    self.curState = "FrontView"

                CS=strCurFingereState
                if self.curState == "FrontView":
                    self._dZoom = -3;

                    if CS[0]=="0" and CS[1]=="1" and CS[2]=="0" and CS[3]=="0" and CS[4]=="0":
                        self._RotateX=0
                        self._RotateY=0
                        self._RotateZ=0
                    elif CS[0] == "0" and CS[1] == "1" and CS[2] == "1" and CS[3] == "0" and CS[4] == "0":
                        self._RotateX = 0
                        self._RotateY = 180
                        self._RotateZ = 0
                    elif CS[0] == "0" and CS[1] == "1" and CS[2] == "1" and CS[3] == "1" and CS[4] == "0":
                        self._RotateX=0
                        self._RotateY=90
                        self._RotateZ=0
                    elif CS[0] == "0" and CS[1] == "1" and CS[2] == "1" and CS[3] == "1" and CS[4] == "1":
                        self._RotateX=0
                        self._RotateY=-90
                        self._RotateZ=0
                    elif CS[0] == "1" and CS[1] == "1" and CS[2] == "1" and CS[3] == "1" and CS[4] == "1":
                        self._RotateX=90
                        self._RotateY=0
                        self._RotateZ=0
                    elif CS[0] == "1" and CS[1] == "0" and CS[2] == "0" and CS[3] == "0" and CS[4] == "1":
                        self._RotateX=-90
                        self._RotateY=0
                        self._RotateZ=0
                elif self.curState == "Move":
                    dStep = 0.005
                    dDiffX = 0
                    dDiffY = 0
                    if CS[0]=="0" and CS[1]=="1" and CS[2]=="0" and CS[3]=="0" and CS[4]=="0":
                        dDiffX = -dStep
                        dDiffY = 0
                    elif CS[0] == "0" and CS[1] == "1" and CS[2] == "1" and CS[3] == "0" and CS[4] == "0":
                        dDiffX = dStep
                        dDiffY = 0
                    elif CS[0] == "0" and CS[1] == "1" and CS[2] == "1" and CS[3] == "1" and CS[4] == "0":
                        dDiffX = 0
                        dDiffY = dStep
                    elif CS[0] == "0" and CS[1] == "1" and CS[2] == "1" and CS[3] == "1" and CS[4] == "1":
                        dDiffX = 0
                        dDiffY = -dStep

                    self._dMoveX+=dDiffX
                    self._dMoveY+=dDiffY
                elif self.curState == "Rotate":
                    dStep = 1
                    dDiffX = 0
                    dDiffY = 0
                    dDiffZ = 0

                    if CS[0] == "1":
                        dStep=-dStep
                    if CS[1] == "1":
                        dDiffX=dStep
                    if CS[2] == "1":
                        dDiffY=dStep
                    if CS[3] == "1":
                        dDiffZ=dStep
                    self._RotateX +=dDiffX
                    self._RotateY +=dDiffY
                    self._RotateZ +=dDiffZ
                elif self.curState == "Zoom":
                    dStep = 0.02
                    dDiff = 0
                    if CS[0]=="0" and CS[1]=="1" and CS[2]=="0" and CS[3]=="0" and CS[4]=="0":
                        dDiff = -dStep
                    if CS[0]=="1" and CS[1]=="1" and CS[2]=="0" and CS[3]=="0" and CS[4]=="0":
                        dDiff = dStep
                    self._dZoom+=dDiff
                    if self._dZoom>-1.5:
                        self._dZoom=-1.5
                    elif self._dZoom<-15:
                        self._dZoom = -15

    # Box 0.1-0.2ms
    def DrawBox(self):
        halfLen=self.mappingWidth

        glBindTexture(GL_TEXTURE_2D, 0)
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 1.0);        glVertex3f(-halfLen,halfLen,halfLen)
        glTexCoord2f(0.0, 0.0);        glVertex3f(-halfLen,-halfLen,halfLen)
        glTexCoord2f(1.0, 0.0);        glVertex3f(halfLen,-halfLen,halfLen)
        glTexCoord2f(1.0, 1.0);        glVertex3f(halfLen,halfLen,halfLen)
        glEnd()

        #face2
        glBindTexture(GL_TEXTURE_2D, 1)
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 1.0);        glVertex3f(halfLen,halfLen,-halfLen)
        glTexCoord2f(0.0, 0.0);        glVertex3f(halfLen,-halfLen,-halfLen)
        glTexCoord2f(1.0, 0.0);        glVertex3f(-halfLen,-halfLen,-halfLen)
        glTexCoord2f(1.0, 1.0);        glVertex3f(-halfLen,halfLen,-halfLen)
        glEnd()

        #face3
        glBindTexture(GL_TEXTURE_2D, 2)
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 1.0);        glVertex3f(-halfLen,halfLen,-halfLen)
        glTexCoord2f(0.0, 0.0);        glVertex3f(-halfLen,-halfLen,-halfLen)
        glTexCoord2f(1.0, 0.0);        glVertex3f(-halfLen,-halfLen,halfLen)
        glTexCoord2f(1.0, 1.0);        glVertex3f(-halfLen,halfLen,halfLen)
        glEnd()

        #face4
        glBindTexture(GL_TEXTURE_2D, 3)
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 1.0);        glVertex3f(halfLen,halfLen,halfLen)
        glTexCoord2f(0.0, 0.0);        glVertex3f(halfLen,-halfLen,halfLen)
        glTexCoord2f(1.0, 0.0);        glVertex3f(halfLen,-halfLen,-halfLen)
        glTexCoord2f(1.0, 1.0);        glVertex3f(halfLen,halfLen,-halfLen)
        glEnd()

        #face5
        glBindTexture(GL_TEXTURE_2D, 4)
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 1.0);        glVertex3f(-halfLen,halfLen,-halfLen)
        glTexCoord2f(0.0, 0.0);        glVertex3f(-halfLen,halfLen,halfLen)
        glTexCoord2f(1.0, 0.0);        glVertex3f(halfLen,halfLen,halfLen)
        glTexCoord2f(1.0, 1.0);        glVertex3f(halfLen,halfLen,-halfLen)
        glEnd()

        #face6
        glBindTexture(GL_TEXTURE_2D, 5)
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 1.0);        glVertex3f(-halfLen,-halfLen,halfLen)
        glTexCoord2f(0.0, 0.0);        glVertex3f(-halfLen,-halfLen,-halfLen)
        glTexCoord2f(1.0, 0.0);        glVertex3f(halfLen,-halfLen,-halfLen)
        glTexCoord2f(1.0, 1.0);        glVertex3f(halfLen,-halfLen,halfLen)
        glEnd()

    #LoadTexture
    def LoadTexture(self):
        listHideFaces=[]
        if self.curState!="Initial":
            self.FaceBlankingBox.SetRotation(self._RotateX,self._RotateY,self._RotateZ)
            listHideFaces=self.FaceBlankingBox.GetHideFaces()

        self.CreateOneTexture(listHideFaces,0,self.cap1,self.frameCount1)
        self.CreateOneTexture(listHideFaces,1,self.cap2,self.frameCount2)
        self.CreateOneTexture(listHideFaces,2,self.cap3,self.frameCount3)
        self.CreateOneTexture(listHideFaces,3,self.cap4,self.frameCount4)
        self.CreateOneTexture(listHideFaces,4,self.cap5,self.frameCount5)
        self.CreateOneTexture(listHideFaces,5,self.cap6,self.frameCount6)
    def CreateOneTexture(self,listHideFaces,i,cap,frameCount):
        if i in listHideFaces:
            glGenTextures(2)
            glBindTexture(GL_TEXTURE_2D, i)
            return None

        if cap.get(cv2.CAP_PROP_POS_FRAMES) == frameCount:    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        success, img = cap.read()
        if success==False:
            return None
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)
        img=cv2.flip(img,0)

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


    #MainLoop
    def MainLoop(self):
        glutMainLoop()

if __name__ == '__main__':
    w = ARIASMain()
    t = threading.Thread(target=w.GetHandPoints)
    t.start()
    w.MainLoop()




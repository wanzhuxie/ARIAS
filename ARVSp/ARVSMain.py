# !/usr/bin/python
# -*- coding: utf-8 -*-

# -------------------------------------------
#
# -------------------------------------------

from OpenGL.GL import *
from OpenGL.GLUT import *
import cv2
import sys
from OpenGL.GLU import *
from PIL import Image
class ARVSMain:
    def __init__(self,
        width=640,
        height=480,
        title='ARVS'.encode()):

        glutInit(sys.argv)
        glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
        glutInitWindowSize(width, height)
        self.window = glutCreateWindow(title)
        glutDisplayFunc(self.Draw)
        glutIdleFunc(self.Draw)
        self.InitGL(width, height)

        #绕各坐标轴旋转的角度
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0

        self.cap1 = cv2.VideoCapture("video1.mp4")#"video0.mp4"
        self.cap2 = cv2.VideoCapture("video2.mp4")#"video0.mp4"
        self.cap3 = cv2.VideoCapture("video3.mp4")#"video0.mp4"
        self.cap4 = cv2.VideoCapture("video4.mp4")#"video0.mp4"
        self.cap5 = cv2.VideoCapture("video5.mp4")#"video0.mp4"
        self.cap6 = cv2.VideoCapture("video6.mp4")#"video0.mp4"

        self.Mp=GetHandPoints
    # 绘制图形
    def Draw(self):
        self.LoadTexture()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glLoadIdentity()

        #沿z轴平移
        glTranslate(0.0, 0.0, -5.0)

        #分别绕x,y,z轴旋转
        glRotatef(self.x, 1.0, 0.0, 0.0)
        glRotatef(self.y, 0.0, 1.0, 0.0)
        glRotatef(self.z, 0.0, 0.0, 1.0)

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

        #刷新屏幕，产生动画效果
        glutSwapBuffers()

        #修改各坐标轴的旋转角度
        self.x += 0.2
        self.y += 0.4
        self.z += 0.6

    #加载纹理
    def LoadTexture(self):
        # 提前准备好的6个图片
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

    def InitGL(self, width, height):
        #self.LoadTexture()
        glEnable(GL_TEXTURE_2D)
        glClearColor(1.0, 1.0, 1.0, 0.0)
        glClearDepth(1.0)
        glDepthFunc(GL_LESS)
        glShadeModel(GL_SMOOTH)

        #背面剔除，消隐
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        glEnable(GL_POINT_SMOOTH)
        glEnable(GL_LINE_SMOOTH)
        glEnable(GL_POLYGON_SMOOTH)
        glMatrixMode(GL_PROJECTION)
        glHint(GL_POINT_SMOOTH_HINT,GL_NICEST)
        glHint(GL_LINE_SMOOTH_HINT,GL_NICEST)
        glHint(GL_POLYGON_SMOOTH_HINT,GL_FASTEST)
        glLoadIdentity()
        gluPerspective(45.0, float(width)/float(height), 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)

    def MainLoop(self):
        glutMainLoop()

if __name__ == '__main__':
    w = ARVSMain()
    w.MainLoop()



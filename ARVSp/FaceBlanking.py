# !/usr/bin/python
# -*- coding: utf-8 -*-

# -------------------------------------------
'''
===立方体背面消隐算法===
==Robert方法==0.4ms
面的外法线方向与Z方向夹角<90可见
'''
# -------------------------------------------

import numpy as np
import copy

class FaceBlankingBox:
    def __init__(self,center=[0,0,0],sideLen=2):
        self.center=center
        self.sideLen=sideLen
        self._RotateX = 0.0
        self._RotateY = 0.0
        self._RotateZ = 0.0

        #8个顶点的坐标
        self.listVertexCoor=[]
        self.listVertexInitialCoor=[[-1,1,1],[-1,-1,1],[1,-1,1],[1,1,1],[1,1,-1],[1,-1,-1],[-1,-1,-1],[-1,1,-1]]
        # 立方体每个面的顶点序号 前方面的点序号1234 后方面的点序号5678
        # 面的序号：前0后1左2右3上4下5
        self.listFaceVertex=[[0, 1, 2, 3], \
                             [4, 5, 6, 7], \
                             [7, 6, 1, 0], \
                             [3, 2, 5, 4], \
                             [7, 0, 3, 4], \
                             [1, 6, 5, 2]]

    #设置旋转角度
    def SetRotation(self,x,y,z):
        self._RotateX = x
        self._RotateY = y
        self._RotateZ = z

    #更新旋转后的顶点坐标
    def UpdateVertexCoor(self):
        self.listVertexCoor=copy.deepcopy(self.listVertexInitialCoor)
        #print("======================")
        #print(self.listVertexCoor)
        sinX=np.sin(self._RotateX/180*np.pi)
        sinY=np.sin(self._RotateY/180*np.pi)
        sinZ=np.sin(self._RotateZ/180*np.pi)
        cosX=np.cos(self._RotateX/180*np.pi)
        cosY=np.cos(self._RotateY/180*np.pi)
        cosZ=np.cos(self._RotateZ/180*np.pi)
        for point in self.listVertexCoor:
            #print("ori:", point)
            # 绕X旋转
            x,y,z=point[0],point[1],point[2]
            point[0]=x
            point[1]=y*cosX-z*sinX
            point[2]=y*sinX+z*cosX
            # 绕Y旋转
            x,y,z=point[0],point[1],point[2]
            point[0]=z*sinY+x*cosY
            point[1]=y
            point[2]=z*cosY-x*sinY
            # 绕Z旋转
            x,y,z=point[0],point[1],point[2]
            point[0]=x*cosZ-y*sinZ
            point[1]=x*sinZ+y*cosZ
            point[2]=z
            #print("new:",point)
        #print(self.listVertexCoor)

    # 面的外法线方向与Z方向夹角<90可见
    def GetHideFaces(self):
        self.UpdateVertexCoor()
        listHidenFaces = []
        for j in range (len(self.listFaceVertex)):#遍历每个面
            listFaceVertexIndex=self.listFaceVertex[j]
            mFaceVertex1 = self.listVertexCoor[listFaceVertexIndex[1]]
            mFaceVertex2 = self.listVertexCoor[listFaceVertexIndex[2]]
            mFaceVertex3 = self.listVertexCoor[listFaceVertexIndex[3]]

            planeVector = np.cross(np.array(mFaceVertex2) - np.array(mFaceVertex1),np.array(mFaceVertex3) - np.array(mFaceVertex1))
            if np.dot(planeVector,(0,0,1))<=0:
                listHidenFaces.append(j)
        #print(listHidenFaces)
        return listHidenFaces


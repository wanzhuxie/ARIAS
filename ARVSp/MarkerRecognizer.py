# !/usr/bin/python
# -*- coding: utf-8 -*-

'''
-------------------------------------------
MarkerRecognizer
-------------------------------------------
'''

import sys
import cv2
import numpy as np
from GeneralFunctions import *


class MarkerRecognizer:
    def __init__(self):
        self.img=None
        self.iCellSize = 10
        self.iCellCount = 5
        self.iCellCountWithFrame = self.iCellCount + 2
        self.iMarkerSize = self.iCellCountWithFrame * self.iCellSize

        self.iStandardMarker=np.array([[0, 0],
                              [0, self.iMarkerSize],
                              [self.iMarkerSize, self.iMarkerSize],
                              [self.iMarkerSize, 0]])

    def PreProcess(self,img):
        #img_gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        preResult=cv2.Canny(img, 50, 100)
        return preResult
    def PreProcess2(self,img):
        img_gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        #img_gray=cv2.Canny(img_gray, 50, 100)
        thresh_size = (50//4)*2 + 1
        img_adaptiveThreshold=cv2.adaptiveThreshold(img_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY , thresh_size, thresh_size*0.8)#THRESH_BINARY_INV
        kernel=np.ones((3,3),np.uint8)
        preResult=cv2.erode(img_adaptiveThreshold,kernel)
        #cv2.imshow("img_gray",img_gray)
        cv2.imshow("img_adaptiveThreshold",img_adaptiveThreshold)
        #cv2.imshow("preResult",preResult)
        return preResult

    def DetectPossibleMarker(self,img):
        preResult=self.PreProcess(img)
        cv2.imshow("preResult",preResult)


        listPossibleMarkers=[]
        contours, hierarchy = cv2.findContours(preResult,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
        for i in range(len(contours)):
            #print(contours[i])
            length=cv2.arcLength(contours[i], False)
            area=cv2.contourArea(contours[i])
            #print("%.2f"%length , "," , "%.2f"%area)
            if len(contours[i])<100:
                continue

            #cv2.drawContours(img, contours, i, (255, 0, 0), 2)
            epsilon = 0.02 * cv2.arcLength(contours[i], True)
            approx=cv2.approxPolyDP(contours[i], epsilon , True )

            #print(len(approx))
            #print(cv2.isContourConvex(approx))

            if len(approx) != 4:
                continue
            if not cv2.isContourConvex(approx):
                continue

            #print("-------------------------------")
            #print(approx)
            approx=np.reshape(approx,(-1,2))
            #print("-------------------------------")

            #rect side length
            dLen0=np.sqrt(np.sum(np.square(approx[0] - approx[1])))
            dLen1=np.sqrt(np.sum(np.square(approx[1] - approx[2])))
            dLen2=np.sqrt(np.sum(np.square(approx[2] - approx[3])))
            dLen3=np.sqrt(np.sum(np.square(approx[3] - approx[0])))
            #print(dLen0,dLen1,dLen2,dLen3)
            dMin=min(dLen0,dLen1,dLen2,dLen3)
            dMax=max(dLen0,dLen1,dLen2,dLen3)
            #print(dMin,dMax)

            if dMax>dMin*4 :
                continue

            #print("=========================")
            #print(np.array(approx[1]-approx[0]))
            #print(np.array(approx[2]-approx[0]))
            dAngle_01_02=GetAngle(np.array(approx[1]-approx[0]) , np.array(approx[2]-approx[0]))
            #print ("angle_01-02",dAngle_01_02)

            cv2.polylines(img, [approx], True, (0, 0, 255), 2)
            listPossibleMarkers.append(approx)

        cv2.imshow("Background", img)
        return listPossibleMarkers



    def Recognize(self, img0):
        listPossibleMarkers=self.DetectPossibleMarker(img0)
        img_gray=cv2.cvtColor(img0,cv2.COLOR_BGR2GRAY)

        #cellPixelCount 方块标准像素数
        cellPixelCount=self.iCellSize**2
        #frameSide_Pixel_Threshold  cellPixelCount*7*(4/3) 边框黑色，像素数最多总数700的四分之一
        side_Pixel_Threshold=cellPixelCount*self.iCellCountWithFrame/4
        #
        listRealMarkers = []
        for i in range (len(listPossibleMarkers)):
            #print("===================")
            eachMarker=listPossibleMarkers[i].astype(np.float32)
            standardMarkers=self.iStandardMarker.astype(np.float32)
            #print(eachMarker)
            #print(standardMarkers)
            M=cv2.getPerspectiveTransform(eachMarker,standardMarkers)
            #print(M)

            # extract marker
            image_marker=cv2.warpPerspective(img_gray,M,(self.iMarkerSize, self.iMarkerSize))
            #cv2.imshow("image_marker",image_marker)
            # input img should be gray
            _,marker_threshold=cv2.threshold(image_marker, 180, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
            #cv2.imshow("marker_threshold",marker_threshold)
            kernel = np.ones((3, 3), np.uint8)
            marker_threshold=cv2.erode(marker_threshold,kernel)
            #cv2.imshow("erode",marker_threshold)
            # is it real marker? check cell pixel
            #h,w,c = marker_threshold.shape
            #print("total pixel:",w*h)

            #4 side frames
            sideLen=marker_threshold.shape[1] // self.iCellCountWithFrame
            upper_frame=marker_threshold[:, :sideLen]
            Lower_frame=marker_threshold[:, sideLen*(self.iCellCountWithFrame-1):]
            left__frame=marker_threshold[:sideLen, :]
            right_frame=marker_threshold[sideLen*(self.iCellCountWithFrame-1):, :]
            upper_PixelCount=cv2.countNonZero(upper_frame)
            lower_PixelCount=cv2.countNonZero(Lower_frame)
            left__PixelCount=cv2.countNonZero(left__frame)
            right_PixelCount=cv2.countNonZero(right_frame)
            #print("frame side pixel count:",upper_PixelCount,lower_PixelCount,left__PixelCount,right_PixelCount)

            # note: the algorithms are diff when in PreProcess(Canny,adaptiveThreshold)!!!!!!!!!!!!!!!!!!!!!!
            if upper_PixelCount>side_Pixel_Threshold \
            or lower_PixelCount>side_Pixel_Threshold \
            or left__PixelCount>side_Pixel_Threshold \
            or right_PixelCount>side_Pixel_Threshold:
                continue

            #20220821 continue later!!!!!!!!!!!!!!!
            #get the marker's information

            markerInfo=np.zeros([self.iCellCount,self.iCellCount])
            for x in range (0,self.iCellCount):
                for y in range (0,self.iCellCount):
                    cell_img=marker_threshold[int((y+1)*self.iCellSize):\
                                              int((y+2)*self.iCellSize),\
                                              int((x+1)*self.iCellSize):\
                                              int((x+2)*self.iCellSize)]
                    NonZeroCount = cv2.countNonZero(cell_img)
                    print((x+1),(y+1),"cell_PixelCount",NonZeroCount)
                    if NonZeroCount>cellPixelCount/2:
                        markerInfo[x][y]=1
            print ("===============marker info===============")
            print (markerInfo)
            cv2.imshow("marker",marker_threshold)

            corners=listPossibleMarkers[i]
            ##sub-pixel
            #criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.1)
            #corners = cv2.cornerSubPix(img_gray, corners, (5, 5), (-1, -1), criteria)
            #collect final markers
            listRealMarkers.append(corners)

        return listRealMarkers


if __name__ == '__main__0':
    for x in range(1, 10):
        for y in range(1, 10):
            #cell_img = marker_threshold[y / self.iCellCountWithFrame:(y + 1) / self.iCellCountWithFrame,x / self.iCellCountWithFrame:(x + 1) / self.iCellCountWithFrame]
            print(y / 10 , (y + 1)/10 , x / 10 , (x + 1)/10)


if __name__ == '__main__':
    cap0 = cv2.VideoCapture(0)
    MR=MarkerRecognizer()
    while True:
        _,img=cap0.read()
        img=MR.Recognize(img)


        #cv2.imshow("Background", img)
        cv2.waitKey(100)



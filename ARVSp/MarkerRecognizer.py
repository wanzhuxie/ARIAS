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
    def __init__(self,Test=False):
        self.Test=Test
        self.img=None
        self.iCellSize = 10
        self.iCellCount = 5
        self.iCellCountWithFrame = self.iCellCount + 2
        self.iMarkerSize = self.iCellCountWithFrame * self.iCellSize

        self.iStandardMarker=np.array([[0, 0],
                              [0, self.iMarkerSize],
                              [self.iMarkerSize, self.iMarkerSize],
                              [self.iMarkerSize, 0]])

    #Canny
    def PreProcess(self,img):
        img_gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        #img_gray=cv2.blur(img_gray,(3,3))
        preResult=cv2.Canny(img_gray, 80, 160)
        return preResult
    #adaptiveThreshold
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
        if self.Test:
            cv2.imshow("preResult",preResult)

        listPossibleMarkers=[]
        contours, hierarchy = cv2.findContours(preResult,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
        for i in range(len(contours)):
            #print(contours[i])
            #length=cv2.arcLength(contours[i], False)
            #area=cv2.contourArea(contours[i])
            #print("%.2f"%length , "," , "%.2f"%area)
            if len(contours[i])<100:
                continue

            #corner count is 4 ?
            epsilon = 0.1 * cv2.arcLength(contours[i], True)
            approx=cv2.approxPolyDP(contours[i], epsilon , True )
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
            crossValue_01_02=np.cross(np.array(approx[1]-approx[0]) , np.array(approx[2]-approx[0]))
            print ("angle_01-02",crossValue_01_02)
            if crossValue_01_02<0:
                temp=np.copy(approx[3])
                approx[3]=approx[1]
                approx[1]=temp

            #exist repeat marker?
            bExist=False
            for j in range (len(listPossibleMarkers)):
                dLen00 = np.sqrt(np.sum(np.square(approx[0] - listPossibleMarkers[j][0])))
                dLen11 = np.sqrt(np.sum(np.square(approx[1] - listPossibleMarkers[j][1])))
                dLen22 = np.sqrt(np.sum(np.square(approx[2] - listPossibleMarkers[j][2])))
                dLen33 = np.sqrt(np.sum(np.square(approx[3] - listPossibleMarkers[j][3])))
                dDisThrehold=5
                if dLen00<dDisThrehold and dLen11<dDisThrehold and dLen22<dDisThrehold and dLen33<dDisThrehold:
                    bExist=True
                    break
            if not bExist:
                listPossibleMarkers.append(approx)

        return listPossibleMarkers



    def Recognize(self, img0):
        listPossibleMarkers=self.DetectPossibleMarker(img0)

        #show Possible Markers
        if self.Test:
            imgPossible=img0.copy()
            for i in range (len(listPossibleMarkers)):
                cv2.polylines(imgPossible, [listPossibleMarkers[i]], True, (0, 0, 255), 2)
            cv2.imshow("Possible Markers", imgPossible)


        img_gray=cv2.cvtColor(img0,cv2.COLOR_BGR2GRAY)

        #cellPixelCount 方块标准像素数100
        cellPixelCount=self.iCellSize**2
        #frameSide_Pixel_Threshold  cellPixelCount*7*(4/3) 边框黑色，像素数最多总数700的四分之一
        side_Pixel_Threshold=cellPixelCount*self.iCellCountWithFrame/4

        # final markers
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

            # erode to shrink white cell
            marker_threshold=cv2.erode(marker_threshold,kernel)
            #if self.Test:
                #cv2.imshow("erode",marker_threshold)

            # is it real marker? check cell pixel
            # side frames
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

            # note: the algorithms are diff when PreProcess changed(Canny,adaptiveThreshold)!!!!!!!!!!!!!!!!!!!!!!
            if upper_PixelCount>side_Pixel_Threshold \
            or lower_PixelCount>side_Pixel_Threshold \
            or left__PixelCount>side_Pixel_Threshold \
            or right_PixelCount>side_Pixel_Threshold:
                continue

            #get the marker's information
            markerInfo=np.zeros([self.iCellCount,self.iCellCount])
            for x in range (0,self.iCellCount):
                for y in range (0,self.iCellCount):
                    cell_img=marker_threshold[int((y+1)*self.iCellSize):\
                                              int((y+2)*self.iCellSize),\
                                              int((x+1)*self.iCellSize):\
                                              int((x+2)*self.iCellSize)]
                    NonZeroCount = cv2.countNonZero(cell_img)
                    if NonZeroCount>cellPixelCount/2:
                        markerInfo[x][y]=1

                    #if self.Test:
                        #print((x+1),(y+1),"cell_PixelCount",NonZeroCount)

            #print ("===============marker info===============")
            #print (markerInfo)

            if self.Test:
                markerName="finalMarker-"+str(i)
                cv2.imshow(markerName,marker_threshold)

            corners=listPossibleMarkers[i]
            #collect final markers
            listRealMarkers.append(corners)

        return listRealMarkers



if __name__ == '__main__':
    cap0 = cv2.VideoCapture(0)
    MR=MarkerRecognizer(True)
    while True:
        _,img=cap0.read()
        listRealMarkers=MR.Recognize(img)
        markerCount=len(listRealMarkers)
        if markerCount>0:
            print("===============markerCount===============")
            print("Marker count:",markerCount)
        for i in range (markerCount):
            cv2.polylines(img, [listRealMarkers[i]], True, (0, 0, 255), 2)
            print(listRealMarkers[i])
        cv2.imshow("final markers", img)

        #cv2.imshow("Background", img)
        cv2.waitKey(100)



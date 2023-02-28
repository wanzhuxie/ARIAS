# !/usr/bin/python
# -*- coding: utf-8 -*-

'''-------------------------------------------
GeneralFunctions
-------------------------------------------'''

import cv2
import time
import numpy as np

#a,b are numpy arry [1,0] [0,1]
def GetAbsoluteAngle(a,b):
    normal_a=np.sqrt(np.sum(a*a))
    normal_b=np.sqrt(np.sum(b*b))
    cos_value=np.dot(a,b) / (normal_a*normal_b)
    arccos=np.arccos(cos_value)
    angle=arccos*180/np.pi
    return angle


class Point3D:
    def __init__(self,iX,iY,iZ ):
        self.X=iX
        self.Y=iY
        self.Z=iZ

def AddWeightWithoutWhite(imgMain,ratio1,imgMask,ratio2):
    timePoint1 = time.perf_counter()

    if False:
        hight=imgMain.shape[0]
        width =imgMain.shape[1]
        hight2=imgMask.shape[0]
        width2=imgMask.shape[1]
        if hight!=hight2 or width!=width2:
            return
        for i in range(hight):
            for j in range(width):
                #print(imgMask[i][j])
                if imgMask[i][j][0]!=255 or imgMask[i][j][1]!=255 or imgMask[i][j][2]!=255:
                    imgMain[i][j]=imgMain[i][j]*ratio1+imgMask[i][j]*ratio2
    else:
        imgMain = cv2.addWeighted(imgMain, ratio1, imgMask, ratio2, 0)

    timePoint2=time.perf_counter()
    print ("AddWeightWithoutWhite:", "%.2f" % ((timePoint2-timePoint1)*1000), "ms")

    return imgMain

def AddMaskImg(image,mask,pos,ratio1,ratio2):
    formalmask = np.zeros((image.shape), dtype=np.uint8)
    maskH=mask.shape[0]
    maskW=mask.shape[1]
    posX=pos[0]
    posY=pos[1]
    formalmask[posY:posY+maskH,posX:posX+maskW]=mask
    ori_img_on_mask= image[ posY:posY+maskH,posX:posX+maskW]
    #mask_img = cv2.addWeighted(ori_img_on_mask, ratio1, mask, ratio2, 0)
    mask_img=AddWeightWithoutWhite(ori_img_on_mask, ratio1, mask, ratio2)
    image[posY:posY + maskH,posX:posX + maskW] = mask_img

def AddMasks(image,listMaskImg,listMaskPos,iActiveIndex):
    # 1.读取图片
    for i in range(len(listMaskImg)):
        if i==iActiveIndex:
            AddMaskImg(image,listMaskImg[i],listMaskPos[i],0.2,0.8)
        else:
            AddMaskImg(image,listMaskImg[i],listMaskPos[i],0.8,0.2)

if __name__ == '__main__':
    print((np.cross([1,1],[1,0])))
    print((np.cross([1,1],[1,0])))
    print((np.cross([1,0],[1,1])))
    print((np.cross([1,0],[1,1])))


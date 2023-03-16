# !/usr/bin/python
# -*- coding: utf-8 -*-

# -------------------------------------------
# it supports only one hand currently
# -------------------------------------------

import sys
import numpy as np
class GestureRecognizer:
    def __init__(self,listHandPoints ):
        self.listHandPoints = listHandPoints

    def GetFingerState(self):
        result = ""
        iPointCount = len(self.listHandPoints)
        if iPointCount != 21:
            return ""

        isRightHand = False  # left or right
        if self.listHandPoints[2].X < self.listHandPoints[17].X:
            isRightHand = True

        # ==============Thumb===========
        # -----Thumb condition 1-----
        listPointForPalmDiameter = [0, 1, 2, 3, 5, 6, 9, 10, 13, 14, 17, 18]
        listX = []
        listY = []
        for i in listPointForPalmDiameter:
            listX.append(self.listHandPoints[i].X)
            listY.append(self.listHandPoints[i].Y)
        listX.sort()
        listY.sort()
        diameterX = listX[len(listX) - 1] - listX[0]
        diameterY = listY[len(listY) - 1] - listY[0]
        dPalmDiameter = diameterX
        if diameterY > dPalmDiameter:
            dPalmDiameter = diameterY

        # Judge the min distance between the thumb tip and these points
        listPointForCheckDis = [6, 7, 8, 10, 11, 12, 14, 15, 16, 18, 19, 20]
        listDis = []
        for i in listPointForCheckDis:
            listDis.append(np.abs(self.listHandPoints[i].X - self.listHandPoints[4].X))
            listDis.append(np.abs(self.listHandPoints[i].X - self.listHandPoints[3].X))
        listDis.sort()
        minDis = listDis[0]
        # print("     ",int(dPalmDiameter),"--",np.abs(self.listHandPoints[3].X-self.listHandPoints[4].X)*20,"--",minDis*10)

        # Judge the X distance between 3 and 4. The thumb is closed if it is small
        if np.abs(self.listHandPoints[3].X - self.listHandPoints[4].X) * 20 < dPalmDiameter:
            result = result + "0"
        # Judge the min distance between the thumb tip and these points
        elif minDis * 7 < dPalmDiameter:
            result = result + "0"
        else:  # Otherwise, continue to judge whether it is closed
            if isRightHand:  # right hand
                if self.listHandPoints[4].X < self.listHandPoints[3].X:
                    result = result + "1"
                else:
                    result = result + "0"
            else:  # left hand
                if self.listHandPoints[4].X < self.listHandPoints[3].X:
                    result = result + "0"
                else:
                    result = result + "1"

        # ==============other four============
        for index in [8, 12, 16, 20]:
            if self.listHandPoints[index].Y >= self.listHandPoints[index - 1].Y or self.listHandPoints[index].Y >= \
                    self.listHandPoints[index - 2].Y or self.listHandPoints[index].Y >= self.listHandPoints[index - 3].Y:
                result = result + "0"
            else:
                result = result + "1"

        return result

#if __name__ == '__main__':



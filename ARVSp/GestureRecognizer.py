# !/usr/bin/python
# -*- coding: utf-8 -*-

# -------------------------------------------
#目前只支持单手
# -------------------------------------------

import sys

class GestureRecognizer:
    def __init__(self,listHandPoints ):
        self.listHandPoints = listHandPoints


    def GetFingerState(self):
        result=""
        iPointCount=len(self.listHandPoints)
        if iPointCount!=21:
            return ""

        isRightHand=False #left or right
        if  self.listHandPoints[2].X< self.listHandPoints[17].X:
            isRightHand=True

        #Thunb
        if isRightHand: #right hand
            if  self.listHandPoints[4].X< self.listHandPoints[3].X:
                result=result+"1"
            else:
                result = result + "0"
        else: #left hand
            if  self.listHandPoints[4].X< self.listHandPoints[3].X:
                result=result+"0"
            else:
                result = result + "1"
        #other four
        for index in [8, 12, 16, 20]:
            if  self.listHandPoints[index].Y >=  self.listHandPoints[index-1].Y or  self.listHandPoints[index].Y >=  self.listHandPoints[index-2].Y or  self.listHandPoints[index].Y >=  self.listHandPoints[index-3].Y:
                result = result + "0"
            else:
                result = result + "1"

        return result
#if __name__ == '__main__':



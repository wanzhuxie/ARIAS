# !/usr/bin/python
# -*- coding: utf-8 -*-

'''-------------------------------------------
GeneralFunctions
-------------------------------------------'''

import sys
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

if __name__ == '__main__':
    print((np.cross([1,1],[1,0])))
    print((np.cross([1,1],[1,0])))
    print((np.cross([1,0],[1,1])))
    print((np.cross([1,0],[1,1])))



----------

# ARIAS

ARIAS: An interactive advertising system based on augmented reality.

## Introduction

It is an interactive video playback system based on augmented reality and gesture recognition. The system recognizes the image captured by the camera in real time. When there is a predefined square marker, A cube is created at the marker position, and the pre configured video files are played on the six faces of the cube. The cube can be manipulated through gestures. It can be used for campus publicity, shopping mall guidance, scenic spot introduction, etc.
## Use guide
1. Ensure the computer has at leat one webcamera. Install Python and other external library.
2. Show one marker the webcamera.The markers can be find in "Markers" folder. Now the feedback of the system will contain a virtual box on the marker.
3. 
## Marker definition

1. 5x5 white cells with black background. There are four corners of the marker and only one corner is an isolated cell, that is, the surrounding color is black. The last row and the last column have white cells, that is the sum of the values in the last row and the last column cannot be 0 (black 0, white 1)
2. The marker with isolated cell in the upper left corner is regarded as the standard marker. When the isolated cell is at the other three corners, the marker is considered to be the result of plane rotation on the basis of the standard marker. 

## Software library
 - Python
 - OpenCV
 - OpenGL
 - MeadiaPipe	

## Software architecture

#### General functions
Some common methods for the whole workspace.

#### GestureRecognizer
Recognize the gesture signal.

#### HandPointsProvider
Use MeadiaPipe as the frame for hand key point recognition to extract 2.5D coordinates of 21 key points of the hand. 

#### MarkerRecognizer
To recognize Markers.

#### FaceBlanking
Optimization of box rendering, that is, not rendering the occluded faces.

#### Main program arvsmain

###### Identification of markers
Opencv processes images to identify predefined markers.

###### Creation of virtual graphics
After identifying the marker, calculate the pose of the marker in space, create a cube at the marker using OpenGL, and create an image map captured by the camera in real time on the surface of the cube.

###### Gesture analysis
Analyze the hand key points obtained through the handpointsprovider, calculate the current gesture, and then manipulate the virtual object accordingly.

-Gesture status
1. Initialization status: the program has just been initialized and no marker has been detected
2. Fronting status
3. Translation status
4. Movement status
5. Rotating state
6. Zoom status

-State switching
1. Clench your fist first, then stretch out your five fingers

-Face up operation
1. Front view 1: index finger
2. Front view 2: index finger + middle finger
3. Front view 3: index finger + middle finger + ring finger
4. Front view 4: index finger + middle finger + ring finger + little thumb
5. Front view 5: index finger + middle finger + ring finger + little thumb + thumb
6. Front view 6: Little thumb + thumb

-Pan operation
1. X +: index finger
2. X -: index finger + middle finger
3. Y +: index finger + middle finger + ring finger
4. Y -: index finger + middle finger + ring finger + little thumb

-Rotation operation
1. X +: index finger
2. X -: index finger + thumb
3. Y +: middle finger
4. Y -: middle finger + thumb
5. Z +: ring finger
6. Z -: ring finger + thumb

-Zoom operation
1. Zoom in: index finger
2. Shrinking: index finger + thumb

###### Graphical interface
It is mainly the OpenGL, which is used to display the real world scene acquired by the camera and the scene after the combination of virtual and real. Some controls that can be operated by the mouse are embedded in the form, and the functions are basically the same as gesture operations. However, using the mouse will be more accurate and smoother.

## Instructions for use
Start the program. At this time, the real world scene captured by the camera is displayed in the window.  Display the marker in front of the camera or use the camera scan the marker. At this time, the virtual cube appears in the window. The position and attitude of the cube depend on the position of the marker relative to the camera. At this time, a gesture can be used to intervene. After the intervention, the virtual cube no longer changes with the marker, but is controlled by the operation of the gesture.


----------


# ARVS
交互式广告系统设计

## 简介
基于增强现实及手势识别的交互式视频播放系统，系统实时识别摄像头捕获的图像，当有预定义的正方形标记时，在标记处创建立方体，在立方体的六个面上播放已提前配置好的视频文件，可以通过手势操控立方体。可用于校园宣传、商场指引、景区景点介绍等。

## 标记定义
 1. 5x5黑底白单元格，标记的四个角处有且只有一个角为孤立单元格，即其周围颜色都是黑色。最后一行及最后一列的数值之和不可为0(黑0白1)
 2. 将左上角为孤立单元格的标记视为标准标记，当孤立单元格在其他的三个角处时，认为该标记是在标准标记的基础上平面旋转的结果。最后一行及最后一列均有白色单元格。
## 软件库
 - Python
 - OpenCV
 - OpenGL
 - MeadiaPipe	
## 软件架构
#### GeneralFunctions
一些多模块常用的方法
#### GestureRecognizer
识别所作出的手势信号
#### HandPointsProvider
使用MeadiaPipe为手部关键点识别的框架，提取手部21个关键点的2.5D坐标
#### MarkerRecognizer
识别标记
#### FaceBlanking
对Box渲染时的优化，即不渲染被遮挡的面
#### ARVSMain
主程序
###### 虚拟图形的创建
识别标记后，计算标记在空间的姿态，使用OpenGL在标记处创建立方体，并在立方体表面创建摄像头实时捕获的图像贴图
###### 手势分析
对通过HandPointsProvider得到的手关键点进行分析，计算当前手势，进而对虚拟物体进行相应的操控。
- 手势状态
	1. 初始化状态: 程序刚刚初始化，尚未检测到标记
	2. 正视操作状态
	3. 平移状态
	4. 移动状态
	5. 旋转状态
	6. 缩放状态
- 状态切换
	1. 先握拳再伸开五指
- 正视操作
	1. 正视面1:食指
	2. 正视面2:食指+中指
	3. 正视面3:食指+中指+无名指
	4. 正视面4:食指+中指+无名指+小拇指
	5. 正视面5:食指+中指+无名指+小拇指+大拇指
	6. 正视面6:小拇指+大拇指
- 平移操作
	1. X+:食指
	2. X-:食指+中指
	3. Y+:食指+中指+无名指
	4. Y-:食指+中指+无名指+小拇指
- 旋转操作
	1. X+:食指
	2. X-:食指+大拇指
	3. Y+:中指
	4. Y-:中指+大拇指
	5. Z+:无名指
	6. Z-:无名指+大拇指
- 缩放操作
	1. 放大:食指
	2. 缩小:食指+大拇指	
###### 图形界面
主要为OpenGL窗体，用于展示摄像头获取的真实世界场景及虚实结合后的场景。窗体中嵌入了一些可以用鼠标操作的控件，功能与手势操作基本一致。不过使用鼠标会更精确更顺畅地操控。

## 使用说明
启动程序，此时窗口中显示摄像头实时捕获的真实世界场景，在摄像头前展示标记，或将摄像头对准固定的标记，此时窗口中出现虚拟立方体，立方体的位置及姿态随标记相对于摄像头的位置而定。此时可用手势介入，介入后虚拟物体不再跟随标记而变化，而是受控于手势的操作。

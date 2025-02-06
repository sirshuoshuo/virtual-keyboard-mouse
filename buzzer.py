############# 增加蜂鸣器功能 ###########

## 点击提示：上面的数字点中间，‘L’靠近边缘，点靠下的

import cv2
import numpy as np
import mediapipe as mp
# from Key_map import AllKey
from pynput.keyboard import Controller
import RPi.GPIO as GPIO             # Windows上无法运行,需要换成 winsound函数
import winsound
import time


# 一些初始化
GPIO.setmode(GPIO.BCM)
channel = 12
GPIO.setup(channel, GPIO.OUT)   
notes = {
    '1': 261, '2': 294, '3': 329, '4': 349, '5': 392,
    '6': 440, '7': 493, '8': 523, '9': 587, '0': 659,
    'shift': 1
} 
count = 0        #记录shift按下了多少次

class Key:
    def __init__(self, up_h, up_w, down_h, down_w, name):    # 注意坐标形式（h，w）
        self.down_h = down_h
        self.down_w = down_w
        self.up_h = up_h
        self.up_w = up_w
        self.center = ((down_h+up_h)/2, (down_w+down_w)/2)
        self.keyboard = Controller()
        self.name = name
        
    def is_called(self):
        self.keyboard.type(self.name)
              

# one = Key(51, 108, 86, 169, '1')       #检测不出来，可能要放大范围
one = Key(28, 75, 85, 165, '1')
two = Key(95, 110, 127, 169, '2')
three = Key(137, 105, 173, 167, '3')
four = Key(180, 106, 214, 168, '4')
five = Key(221, 107, 257, 168, '5')
six = Key(266, 109, 299, 165, '6')
seven = Key(307, 104, 343, 164, '7')
eight = Key(350, 103, 387, 164, '8')
nine = Key(393, 103, 430, 164, '9')
zero = Key(434, 104, 474, 162, '0')
Q = Key(69, 181, 103, 243, 'q')
W = Key(113, 184, 149, 242, 'w')
E = Key(155, 183, 191, 242, 'e')
R = Key(197, 182, 234, 242, 'r')
T = Key(240, 180, 276, 242, 't')
Y = Key(284, 180, 319, 240, 'y')
U = Key(326, 182, 362, 242, 'u')
I = Key(369, 179, 407, 239, 'i')
O = Key(415, 181, 447, 238, 'o')
P = Key(452, 180, 492, 239, 'p')
A = Key(81, 256, 115, 320, 'a')
S = Key(123, 258, 157, 318, 's')
D = Key(165, 257, 200, 315, 'd')
F = Key(207, 255, 245, 316, 'f')
G = Key(250, 259, 289, 316, 'g')
H = Key(294, 256, 329, 316, 'h')
J = Key(337, 256, 375, 315, 'j')
K = Key(379, 256, 416, 314, 'k')
L = Key(422, 254, 458, 315, 'l')
Z = Key(102, 333, 135, 394, 'z')
X = Key(144, 333, 183, 393, 'x')
C = Key(187, 331, 224, 393, 'c')
V = Key(230, 333, 269, 394, 'v')
B = Key(276, 330, 310, 390, 'b')
N = Key(318, 330, 354, 392, 'n')
M = Key(359, 332, 396, 391, 'm')
# shift = Key(501, 308, 632, 386, 'shift')   # 右侧shift
shift = Key(10,340,86,392, 'shift')
space = Key(168, 408, 411, 468, ' ')

ALLKey = AllKey = [Q,W,E,R,T,Y,U,I,O,P,A,S,D,F,G,H,J,K,L,Z,X,C,V,B,N,M,one,two,three,four,five,six,seven,eight,nine,zero,shift,space]


class Physical_keyboard:
    def __init__(self):
        self.map = AllKey
        self.w = 480                                                                                                 ##############
        self.h = 640                                                                                                 ##############
        self.pts1 = np.float32([[66,207], [63,453], [521,459], [516,212]])                                     ##############
        self.pts2 = np.float32([[0, 0], [0, self.w], [self.h, self.w], [self.h, 0]])                
        self.M = cv2.getPerspectiveTransform(self.pts1, self.pts2)       # 透视矩阵
        self.R = cv2.getRotationMatrix2D((self.h/2, self.w/2), 180, 1)   # 旋转矩阵
        self.kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        self.board = Controller()
        self.channel = 12      # 蜂鸣器输出引脚
        self.pi_pwm = GPIO.PWM(channel, 1)
        self.pi_pwm.start(0)  
    

    def map_point(self, ch, cw, flag):    # 传入未变换的手指坐标
        global count
        if flag == True:              #好像这个True不用加
            src_point = np.array([[ch, cw, 1]], dtype=np.float32).T  # 原始点齐次坐标
            perspective_point = self.M @ src_point  # 透视变换
            px, py, pz = perspective_point.flatten()
            mapped_point = (px / pz, py / pz)  # 转换为二维坐标

            # 旋转变换
            rotated_point = self.R @ np.array([mapped_point[0], mapped_point[1], 1])  # 旋转变换
            final_point = (rotated_point[0], rotated_point[1])  # 最终映射坐标
            

            for Key in self.map:
                if (final_point[0] > Key.up_h-10) & (final_point[0] < Key.down_h+10) & (final_point[1] > Key.up_w-10) & (final_point[1] < Key.down_w+10):
                    if Key.name == 'shift':
                        count = (count+1)%2

                    if count == 0:
                        print('enter keyboard mode')
                        self.board.type(Key.name)
                        time.sleep(0.6)
                    else:
                        print('enter buzzer mode')
                        if Key.name in {'1','2','3','4','5','6','7','8','9','0'}:
                            frequency = notes[Key.name]
                            # winsound.Beep(frequency, 1500)
                            # time.sleep(0.2)
                            self.pi_pwm.ChangeDutyCycle(50)
                            self.pi_pwm.ChangeFrequency(frequency)
                            time.sleep(0.5)
                            # self.pi_pwm.stop()
                            self.pi_pwm.ChangeDutyCycle(0)
                        else:
                            print('请按下数字按键！')

                    return
            else:
                return



mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_drawing = mp.solutions.drawing_utils

# coding:utf-8
cap = cv2.VideoCapture(0)  # 打开摄像头
keyboard = Physical_keyboard()

z0 = 10000
y0 = 0
x0 = 0
while True:
    ret, frame1 = cap.read()  # 读取视频帧
    if not ret:
        break
    image = cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB)  # 转换颜色空间
    results = hands.process(image)  # 手势识别

    # 处理识别结果
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                frame1,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS) # 用于指定地标如何在图中连接。
            
            i = 0
            for point in hand_landmarks.landmark:
                if i==8:
                    z = int(point.z * frame1.shape[0])    # width
                    x = int(point.x * frame1.shape[1])    # height
                    y = int(point.y * frame1.shape[0])
                    if z0 != 10000:
                        # print('x方向差值:',x-x0)
                        # print('y方向差值:',y-y0)
                        # print('frame[0]:',frame1.shape[0])
                        # print('frame[1]:', frame1.shape[1]
                        print('z方向差值:',z-z0)
                        if z-z0<-15:     #-20
                            if abs(x-x0) <= 14:
                                print("点了")
                                keyboard.map_point(x,y,True)
                            # else:
                            #     pass
            
                    z0 = z
                    x0 = x
                    y0 = y

                    cv2.circle(frame1, (x, y), 5, (0, 255, 0), -1) # 画出关键点
                i = i+1

            

    cv2.imshow('Gesture Recognition', frame1)  # 显示结果
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    time.sleep(0.1)

cap.release()
cv2.destroyAllWindows()
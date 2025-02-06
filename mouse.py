import cv2
import numpy as np
import mediapipe as mp 
import time
import pyautogui
 


def find_dis(x1,y1,x2,y2):
    re = pow(x2 - x1,2)+ pow(y2 - y1,2)
    print(re)
    return re <= 700

#（1）导数视频数据
wScr, hScr = pyautogui.size()   # 返回电脑屏幕的宽和高(1920.0, 1080.0)
wCam, hCam = wScr/2, hScr/2   # 视频显示窗口的宽和高
 
cap = cv2.VideoCapture(0)  # 0代表自己电脑的摄像头
cap.set(3, wCam)  # 设置显示框的宽度1280
cap.set(4, hCam)  # 设置显示框的高度720
 
pTime = 0  # 设置第一帧开始处理的起始时间
 
pLocx, pLocy = 0, 0  # 上一帧时的鼠标所在位置
 
smooth = 1  # 自定义平滑系数，让鼠标移动平缓一些
 
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_drawing = mp.solutions.drawing_utils

 
#（3）处理每一帧图像
while True:
    
    # 图片是否成功接收、img帧图像
    success, img = cap.read()
    
    # 翻转图像，使自身和摄像头中的自己呈镜像关系
    img = cv2.flip(img, flipCode=1)  # 1代表水平翻转，0代表竖直翻转
    img1 = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    #（4）手部关键点检测
    # 传入每帧图像, 返回手部关键点的坐标信息(字典)，绘制关键点后的图像
    results = hands.process(img1) # 上面反转过了，这里就不用再翻转了
    # print(hands)
    
    # 如果能检测到手那么就进行下一步
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                img,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS) # 用于指定地标如何在图中连接。
        # 获取食指指尖坐标，和中指指尖坐标
        i = 0
        for point in hand_landmarks.landmark:
            if i==8:
                x1 = int(point.x * img.shape[1])
                y1 = int(point.y * img.shape[0])
            elif i==4:
                x2 = int(point.x * img.shape[1])
                y2 = int(point.y * img.shape[0])
            i = i+1
        
            
        # 开始移动时，在食指指尖画一个圆圈，看得更清晰一些
        cv2.circle(img, (x1,y1), 15, (255,255,0), cv2.FILLED)  # 颜色填充整个圆
 
        #（6）确定鼠标移动的范围
        # 将食指的移动范围从预制的窗口范围，映射到电脑屏幕范围
        x3 = np.interp(x1, (0, wCam), (0, wScr))
        y3 = np.interp(y1, (0, hCam), (0, hScr))
 
        #（7）平滑，使手指在移动鼠标时，鼠标箭头不会一直晃动
        cLocx = pLocx + (x3 - pLocx) / smooth  # 当前的鼠标所在位置坐标
        cLocy = pLocy + (y3 - pLocy) / smooth            
      
        #（8）移动鼠标
        pyautogui.moveTo(cLocx, cLocy,duration=0.1)  # 给出鼠标移动位置坐标
            
        # 更新前一帧的鼠标所在位置坐标，将当前帧鼠标所在位置，变成下一帧的鼠标前一帧所在位置
        pLocx, pLocy = cLocx, cLocy
 
        #（9）如果食指和中指都竖起，指尖距离小于某个值认为是点击鼠标
        if find_dis(x1,y1,x2,y2):  # 食指和中指都竖起
            pyautogui.mouseDown(x3, y3)
        else: 
            pyautogui.mouseUp()
 
    #（10）显示图像
    # 查看FPS
    cTime = time.time() #处理完一帧图像的时间
    fps = 1/(cTime-pTime)
    pTime = cTime  #重置起始时间
    
    # 在视频上显示fps信息，先转换成整数再变成字符串形式，文本显示坐标，文本字体，文本大小
    cv2.putText(img, str(int(fps)), (70,50), cv2.FONT_HERSHEY_PLAIN, 3, (255,0,0), 3)  
    
    # 显示图像，输入窗口名及图像数据
    cv2.imshow('image', img)    
    if cv2.waitKey(1) & 0xFF==27:  #每帧滞留20毫秒后消失，ESC键退出
        break
 
# 释放视频资源
cap.release()
cv2.destroyAllWindows()
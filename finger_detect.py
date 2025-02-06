############ 目前希望根据得到的变换矩阵找到手指端的坐标
### 这是目前最新的函数和数据 0：19

import cv2
import numpy as np
camera = cv2.VideoCapture(1)

def mouse_callback(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:  
        print(f"Mouse clicked at: ({x}, {y})")
        # 在图像上标记点击位置
        cv2.circle(param, (x, y), 5, (255, 0, 0), -1)
        cv2.putText(param, f"({x},{y})", (x + 10, y - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        cv2.imshow("Keyboard View", param)

class Camera_View:
    def __init__(self):
        # self.image_origin = cv2.imread('finger_test.png')    
        self.w = 480                                                                                                 ##############
        self.h = 640                                                                                                 ##############
        self.pts1 = np.float32([[41, 69], [4, 367], [623, 387], [595, 85]])                                       ##############
        self.pts2 = np.float32([[0, 0], [0, self.w], [self.h, self.w], [self.h, 0]])                
        self.M = cv2.getPerspectiveTransform(self.pts1, self.pts2)       # 透视矩阵
        self.R = cv2.getRotationMatrix2D((self.h/2, self.w/2), 180, 1)   # 旋转矩阵
        self.kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))

    # 图像二值化，透视，旋转
    def image_init(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # gray2 = cv2.adaptiveThreshold(gray, 255,  cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)  # 二值化，可以换函数            ##############
        retval2, simple_threshold_frame_basic = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY)            # 160在正常照明下手指端分别明显
        wrapped_gray2 = cv2.warpPerspective(simple_threshold_frame_basic, self.M, (self.h, self.w))     # 透视
        rotated_gray2 = cv2.warpAffine(wrapped_gray2, self.R, (self.h, self.w))         #旋转
        return rotated_gray2
    
    def map_point(self, x, y):
        # 透视变换
        src_point = np.array([[x, y, 1]], dtype=np.float32).T  # 原始点齐次坐标
        perspective_point = self.M @ src_point  # 透视变换
        px, py, pz = perspective_point.flatten()
        mapped_point = (px / pz, py / pz)  # 转换为二维坐标

        # 旋转变换
        rotated_point = self.R @ np.array([mapped_point[0], mapped_point[1], 1])  # 旋转变换
        final_point = (rotated_point[0], rotated_point[1])  # 最终映射坐标

        return final_point

    # 查找轮廓及轮廓中心坐标
    def find_center(self, rotated_gray2):
        contours, _ = cv2.findContours(rotated_gray2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)  # 寻找轮廓                    ##############
        img_with_contours = cv2.cvtColor(rotated_gray2, cv2.COLOR_GRAY2BGR)  # 转为彩色以便绘制彩色图形                  ### 轮廓找的太少        

        for contour in contours:
            # 绘制轮廓
            cv2.drawContours(img_with_contours, [contour], -1, (0, 0, 255), 2)

            # 计算轮廓的矩
            M = cv2.moments(contour)
            if M["m00"] != 0:
                # 计算质心
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])

                # 绘制中心点
                cv2.circle(img_with_contours, (cx, cy), 5, (0, 255, 0), -1)
                cv2.putText(img_with_contours, f"({cx}, {cy})", (cx + 10, cy - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)

        return img_with_contours


try:
    view = Camera_View()
    while True:
        ret1, frame = camera.read()         # 获取当前帧截图
        view_frame = view.image_init(frame)
        # frame_with_center = view.find_center(view_frame)
        cv2.imshow('simple_basic', view_frame)
        # cv2.imshow('finger_view', frame_with_center)
        # cv2.setMouseCallback("Keyboard View", mouse_callback, simple_threshold_frame_basic)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            camera.release()
            cv2.destroyAllWindows()

except KeyboardInterrupt:
    camera.release()
    cv2.destroyAllWindows()


# 选不同的二值化函数对比效果
        # adaptive_threshold_frame = cv2.adaptiveThreshold(gray_frame, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 35, 3)     
        # retval, simple_threshold_frame_improve = cv2.threshold(gray_frame, 145, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)          # 阈值为150
        # retval2, simple_threshold_frame_basic = cv2.threshold(gray_frame, 160, 255, cv2.THRESH_BINARY)            # 160在正常照明下手指端分别明显 
        
        # adaptive没有明显的黑白区分，把全黑的放上去也是白色居多，可能用不了



####### 效果一般 #######
##### 检测到的点太多了 ######
##### 但是图像的变换还可以 ###
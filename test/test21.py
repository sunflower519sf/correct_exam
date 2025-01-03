import cv2
import numpy as np


image = cv2.imread("test.jpg")

# 影像預處理
def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) # 灰階
    # 高斯模糊
    blurred_image = cv2.GaussianBlur(gray, (5, 5), 0)
    # 使用二值化
    _, binary_image = cv2.threshold(blurred_image, 200, 255, cv2.THRESH_BINARY)
    # 反轉圖片（黑色變白色，白色變黑色）
    inverted_image = cv2.bitwise_not(binary_image)

    
    

    return inverted_image

gray = preprocess_image(image)
cv2.imwrite("gray.jpg", gray)

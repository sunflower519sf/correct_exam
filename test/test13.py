import cv2
import numpy as np

# 影像預處理
def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) # 灰階
    thresh = cv2.adaptiveThreshold(gray, 255, 
                                cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                cv2.THRESH_BINARY_INV, 11, 2) # 二值化並反轉
    return thresh

image = cv2.imread('ggimg/5_0.png')
thresh = preprocess_image(image)
ans_img_dilated = cv2.dilate(thresh, None, iterations=10)
total_pixels = ans_img_dilated.size
# cv2.imshow('ans_img_dilated', ans_img_dilated)
# cv2.waitKey(0)
white_pixels = np.sum(ans_img_dilated > 200)
print(white_pixels/total_pixels*100)

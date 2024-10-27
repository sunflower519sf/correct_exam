import cv2
import numpy as np

def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) # 灰階
    thresh = cv2.adaptiveThreshold(gray, 255, 
                                cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                cv2.THRESH_BINARY_INV, 11, 2) # 二值化並反轉
    return thresh


img = preprocess_image(cv2.imread('output.png'))
img2 = preprocess_image(cv2.imread('minus_blank.png'))
# output = cv2.absdiff(img, img2)
# _, output = cv2.threshold(output, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
output = cv2.subtract(img, img2)
cv2.imshow('out', output)
cv2.waitKey(0)       # 按下任意鍵停止
cv2.destroyAllWindows()
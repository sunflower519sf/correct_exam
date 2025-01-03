import cv2
import numpy as np


# 影像預處理
def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) # 灰階
    thresh = cv2.adaptiveThreshold(gray, 255, 
                                cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                cv2.THRESH_BINARY_INV, 11, 2) # 二值化並反轉
    return thresh



# Load image, grayscale, Gaussian blur, Otsu's threshold
image = cv2.imread('test.png')
thimg = preprocess_image(image)
thimg = cv2.cvtColor(thimg, cv2.COLOR_GRAY2BGR)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
blur = cv2.GaussianBlur(gray, (3,3), 0)
thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

# Detect horizontal lines
horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (100,1))
horizontal_mask = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=1)

# Detect vertical lines
vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1,100))
vertical_mask = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, vertical_kernel, iterations=1)

# Combine masks and remove lines
table_mask = cv2.bitwise_or(horizontal_mask, vertical_mask)
image[np.where(table_mask==255)] = [255,255,255]

thimg[np.where(table_mask==255)] = [0,0,0]




cv2.imshow('thresh', thresh)
cv2.imshow('horizontal_mask', horizontal_mask)
cv2.imshow('vertical_mask', vertical_mask)
cv2.imshow('table_mask', table_mask)
cv2.imshow('image', image)
cv2.imwrite('out.png', thimg)
cv2.waitKey()
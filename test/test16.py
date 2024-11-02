import cv2
import numpy as np

img = cv2.imread('img/ans.png')
img = cv2.resize(img, (600, 650))

# 影像預處理
def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) # 灰階
    thresh = cv2.adaptiveThreshold(gray, 255, 
                                cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                cv2.THRESH_BINARY_INV, 11, 2) # 二值化並反轉
    return thresh

image = preprocess_image(img)


vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1,5))
horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5,1))
remove_horizontal = cv2.morphologyEx(image, cv2.MORPH_OPEN, vertical_kernel)
remove_vertical = cv2.morphologyEx(image, cv2.MORPH_OPEN, horizontal_kernel)


cnts = cv2.findContours(remove_vertical, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cnts = cnts[0] if len(cnts) == 2 else cnts[1]

mask = np.ones(image.shape, dtype=np.uint8)
for c in cnts:
    area = cv2.contourArea(c)
    if area > 50:
        cv2.drawContours(mask, [c], -1, (255,255,255), -1)

kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3,3))
mask = cv2.dilate(mask, kernel, iterations=1)
image = 255 - image
result = 255 - cv2.bitwise_and(mask, image)

# cv2.imshow('result', result)
# cv2.imwrite('result.png', result)
# cv2.imwrite('mask.png', mask)
# cv2.imwrite('image.png', image)



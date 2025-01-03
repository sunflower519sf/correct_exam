import numpy as np 

import cv2 

from matplotlib import pyplot as plt 

image = cv2.imread('testa.jpg')

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# 高斯模糊
blurred_image = cv2.GaussianBlur(image, (5, 5), 0)
# 使用二值化
_, binary_image = cv2.threshold(blurred_image, 100, 255, cv2.THRESH_BINARY)

# 反轉圖片（黑色變白色，白色變黑色）
inverted_image = cv2.bitwise_not(binary_image)

# 顯示結果
# cv2.imshow('Binary Image', binary_image)
cv2.imwrite('out.jpg', inverted_image)
# cv2.imshow('Inverted Image', inverted_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
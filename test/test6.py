import cv2
import numpy as np


# 計算兩點距離
def calculate_the_distance_between_2_points(points1, points2):
    return ((points2[0] - points1[0]) ** 2 + (points2[1] - points1[1]) ** 2) ** 0.5

# 影像預處理
def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) # 灰階
    thresh = cv2.adaptiveThreshold(gray, 255, 
                               cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                               cv2.THRESH_BINARY_INV, 11, 2) # 二值化並反轉
    return thresh




# 讀取影像
image = cv2.imread("test.png")


# 影像預處理
thresh = preprocess_image(image)


# # 二值化
# thresholded_image = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
# # 反轉
# inverted_image = cv2.bitwise_not(thresholded_image)

# 膨脹 # iterations=1 可以改成自定義
dilated_image = cv2.dilate(thresh, None, iterations=1) 



# 找出輪廓
contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
# image_with_all_contours = image.copy()
# cv2.drawContours(image_with_all_contours, contours, -1, (0, 255, 0), 3)

# 過濾輪廓並找出矩形
rectangular_contours = []
for contour in contours:
    peri = cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
    
    if len(approx) == 4:
        rectangular_contours.append(approx)
# Below lines are added to show all rectangular contours
# This is not needed, but it is useful for debugging
# image_with_only_rectangular_contours = image.copy()
# cv2.drawContours(image_with_only_rectangular_contours, rectangular_contours, -1, (0, 255, 0), 3)


tody_lines_list = np.array(rectangular_contours).reshape(len(rectangular_contours), 4, 2)
print(tody_lines_list)
points = tody_lines_list[0]
# for i in rectangular_contours:
#     area = cv2.contourArea(i)
#     print(i, area)

image_with_only_rectangular_contours = image.copy()
cv2.drawContours(image_with_only_rectangular_contours, tody_lines_list, -1, (0, 255, 0), 3)
cv2.imwrite("image_with_only_rectangular_contours.jpg", image_with_only_rectangular_contours)
cv2.imshow('image_with_only_rectangular_contourss', image_with_only_rectangular_contours)
cv2.waitKey(0)



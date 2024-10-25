import ddddocr
import os
import cv2
import numpy as np


# 計算兩點距離
def calculate_the_distance_between_2_points(points1, points2):
    return ((points2[0] - points1[0]) ** 2 + (points2[1] - points1[1]) ** 2) ** 0.5

# 影像預處理
def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) # 灰階
    # 高斯模糊去除雜訊，讓邊緣偵測更加平滑
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(gray, 255, 
                               cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                               cv2.THRESH_BINARY_INV, 11, 2) # 二值化並反轉
    return thresh

def get_img_str(result):
    s = ""
    for i in result['probability']:
        s += result['charsets'][i.index(max(i))]
    return s

# 載入檢測模型
ocr_beta = ddddocr.DdddOcr(beta=True)
ocr_issu = ddddocr.DdddOcr()
# 指定範圍 減少錯誤
ocr_beta.set_ranges("ABCDabcdEe")
ocr_issu.set_ranges("ABCDabcdEe")
# 要求使用 probability=True (其他人提出的問題得知)
# result = ocr.classification(image, probability=True)
# s = ""
# for i in result['probability']:
#     s += result['charsets'][i.index(max(i))]




# 讀取影像
image = cv2.imread("gg.png")


# 影像預處理
thresh = preprocess_image(image)


# # 二值化
# thresholded_image = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
# # 反轉
# inverted_image = cv2.bitwise_not(thresholded_image)

# 膨脹 # iterations=1 可以改成自定義
dilated_image = cv2.dilate(thresh, None, iterations=1) 



# 找出輪廓
contours, hierarchy = cv2.findContours(dilated_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
image_with_all_contours = image.copy()
cv2.drawContours(image_with_all_contours, contours, -1, (0, 255, 0), 3)

# 過濾輪廓並找出矩形
rectangular_contours = []
for contour in contours:
    peri = cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
    if len(approx) == 4:
        rectangular_contours.append(approx)
# Below lines are added to show all rectangular contours
# This is not needed, but it is useful for debugging
image_with_only_rectangular_contours = image.copy()
cv2.drawContours(image_with_only_rectangular_contours, rectangular_contours, -1, (0, 255, 0), 3)

# 找出最大輪廓
max_area = 0
contour_with_max_area = None
for contour in rectangular_contours:
    area = cv2.contourArea(contour)
    if area > max_area:
        max_area = area
        contour_with_max_area = contour
# Below lines are added to show the contour with max area
# This is not needed, but it is useful for debugging
image_with_contour_with_max_area = image.copy()
cv2.drawContours(image_with_contour_with_max_area, [contour_with_max_area], -1, (0, 255, 0), 3)



# cv2.imshow("image", image)
# cv2.imshow("gray", gray)
# # cv2.imshow("thresholded_image", thresholded_image)
# # cv2.imshow("inverted_image", inverted_image)
cv2.imshow("thresh", thresh)
cv2.imshow("dilated_image", dilated_image)
cv2.imshow("image_with_all_contours", image_with_all_contours)
# cv2.imshow("image_with_only_rectangular_contour", image_with_only_rectangular_contours)
# cv2.imshow("image_with_contour_with_max_area", image_with_contour_with_max_area)
cv2.waitKey(0)



# 重塑矩形
# 把
# [[[x1 y1]]

#  [[x2 y2]]

#  [[x3 y3]]

#  [[x4 y4]]]
# 轉成
# [[x1, y1]
#  [x2, y2]
#  [x3, y3]
#  [x4, y4]]

sorting_pos_pts = np.array(contour_with_max_area).reshape((4, 2))
# 建立一個矩形 其中都是0 
contour_with_max_area_ordered = np.zeros((4, 2), dtype="float32")

# 找出左上角和右下角
sorting_pos_s = [sum(i) for i in sorting_pos_pts]
contour_with_max_area_ordered[0] = sorting_pos_pts[np.argmin(sorting_pos_s)]
contour_with_max_area_ordered[2] = sorting_pos_pts[np.argmax(sorting_pos_s)]

# 找出右上角和左下角
sorting_pos_diff = np.diff(sorting_pos_pts, axis=1)
contour_with_max_area_ordered[1] = sorting_pos_pts[np.argmin(sorting_pos_diff)]
contour_with_max_area_ordered[3] = sorting_pos_pts[np.argmax(sorting_pos_diff)]

# 取得圖像寬度
existing_image_width = image.shape[1]

# 將寬度縮小
existing_image_width_reduced_by_10_percent = int(existing_image_width * 0.9)

# 計算左上角到右上角的距離
distance_between_top_left_and_top_right = calculate_the_distance_between_2_points(contour_with_max_area_ordered[0], contour_with_max_area_ordered[1])
# 計算左上角到左下角的距離
distance_between_top_left_and_bottom_left = calculate_the_distance_between_2_points(contour_with_max_area_ordered[0], contour_with_max_area_ordered[3])

# 計算長寬比
aspect_ratio = distance_between_top_left_and_bottom_left / distance_between_top_left_and_top_right

# 設定新圖像的長寬
new_image_width = existing_image_width_reduced_by_10_percent
new_image_height = int(new_image_width * aspect_ratio)

# 透視變換
perspective_transform_pts1 = np.float32(contour_with_max_area_ordered)
perspective_transform_pts2 = np.float32([[0, 0], [new_image_width, 0], [new_image_width, new_image_height], [0, new_image_height]])
# 計算透視變換矩陣(好像是把pts1映射到pts2)
perspective_transform_matrix = cv2.getPerspectiveTransform(perspective_transform_pts1, perspective_transform_pts2)
# 將它應用到圖像上 perspective_transformed_image就是表格了
perspective_corrected_image = cv2.warpPerspective(image, perspective_transform_matrix, (new_image_width, new_image_height))

# cv2.imshow("perspective_corrected_image", perspective_corrected_image)
# cv2.waitKey(0)

# 將圖片周圍填充白色
# 取得圖像高度
image_height = image.shape[0]
# 計算填充的大小
padding = int(image_height * 0.1)
# 填充圖像
perspective_corrected_image_with_padding = cv2.copyMakeBorder(perspective_corrected_image, padding, padding, padding, padding, cv2.BORDER_CONSTANT, value=[255, 255, 255])

# cv2.imshow("perspective_corrected_image_with_padding", perspective_corrected_image_with_padding)
# cv2.waitKey(0)
# cv2.imwrite("test4_image.jpg", perspective_corrected_image_with_padding)


# 影像預處理
thresh = preprocess_image(perspective_corrected_image_with_padding)

# 使用 Canny 邊緣檢測
edges = cv2.Canny(thresh, 30, 200)
# 使用 Hough 變換檢測線條
min_line_length = perspective_corrected_image_with_padding.shape[1] // 10  # 根據圖片大小自適應
max_line_gap = perspective_corrected_image_with_padding.shape[1] // 50
lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100, minLineLength=min_line_length, maxLineGap=max_line_gap)

# 存放水平、垂直線位置
height, width = perspective_corrected_image_with_padding.shape[:2]
horizontal_lines = []
vertical_lines = []


# 處理檢測到的線條
for line in lines:
    x1, y1, x2, y2 = line[0]
    if abs(y2 - y1) < 10:  # 水平直線
        horizontal_lines.append(y1)
    elif abs(x2 - x1) < 10:  # 垂直直線
        vertical_lines.append(x1)

# 去重並排序線條位置
horizontal_lines = sorted(list(set(horizontal_lines)))
vertical_lines = sorted(list(set(vertical_lines)))


# 定義檢測用的資料
# 設定水平、垂直線的間隔
horizontal_line_spacing = perspective_corrected_image_with_padding.shape[0] / len(horizontal_lines)
vertical_line_spacing = perspective_corrected_image_with_padding.shape[1] / len(vertical_lines)

all_img_save = []
# 根據行列數量切割圖像
for i in range(len(horizontal_lines)-1):
    for j in range(len(vertical_lines)-1):
        # 確定格子的邊界
        y_start = horizontal_lines[i]
        y_end = horizontal_lines[i + 1]
        x_start = vertical_lines[j]
        x_end = vertical_lines[j + 1]

        # 提取每個格子的區域
        roi = perspective_corrected_image_with_padding[y_start:y_end, x_start:x_end]
        
        # 儲存符合大小的影像
        if abs(y_end-y_start) > horizontal_line_spacing and abs(x_end-x_start) > vertical_line_spacing:
            all_img_save.append(roi)


        cv2.rectangle(roi, (0, 0), (x_end - x_start, y_end - y_start), (0, 255, 0), 0)



cv2.imshow("all_img_save", perspective_corrected_image_with_padding)
cv2.waitKey(0)
# 分析切割後的圖片
ct = 0
for img in all_img_save:
    
    
    # 影像預處理
    img_orc = preprocess_image(img)
    # 將圖片周圍填充白色
    # 計算填充的大小
    # padding = int(image_height * 0.1)
    # 填充圖像
    # img_orc = cv2.copyMakeBorder(img_orc, padding, padding, padding, padding, cv2.BORDER_CONSTANT, value=[255, 255, 255])
    
    # cv2.imshow(f"img_{ct}", img_orc)
    # cv2.waitKey(0)

    # 將二值化圖像轉換為字節數組
    is_success, gray_bytes = cv2.imencode('.png', img_orc)
    if not is_success:
        raise ValueError("圖片無法編碼為 bytes 資料")
    
    # 取得文字
    # result_beta = get_img_str(ocr_beta.classification(gray_bytes.tobytes(), probability=True))
    # result_issu = get_img_str(ocr_issu.classification(gray_bytes.tobytes(), probability=True))
    result_beta = ocr_beta.classification(gray_bytes.tobytes())
    result_issu = ocr_issu.classification(gray_bytes.tobytes())
    print(ct, result_beta, result_issu)
    
    
    # cv2.imwrite(f"test/{ct}_{result_beta}_{result_issu}.jpg", img_orc)
    cv2.imwrite(f"test/{ct}_.jpg", img_orc)
    ct+=1
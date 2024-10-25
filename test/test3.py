import cv2
import numpy as np

# 读取图像
image_path = './gg.png'  # 替换为你的图片路径
image = cv2.imread(image_path)

# 检查图像是否成功读取
if image is None:
    print("Error: 無法讀取影像")
    exit()

# 转换成灰度
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# 去噪声
blurred = cv2.GaussianBlur(gray, (5, 5), 0)

# 自适应二值化
thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                               cv2.THRESH_BINARY_INV, 11, 2)

# 找到轮廓
contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# 初始化表格边界
table_contour = None
max_area = 0

# 遍历所有轮廓查找最大的矩形，假设表格是最大的矩形
for cnt in contours:
    approx = cv2.approxPolyDP(cnt, 0.02 * cv2.arcLength(cnt, True), True)
    if len(approx) == 4:  # 确保是矩形
        area = cv2.contourArea(cnt)
        if area > max_area:
            max_area = area
            table_contour = approx

# 提取表格区域
if table_contour is not None:
    x, y, w, h = cv2.boundingRect(table_contour)
    table_roi = image[y:y+h, x:x+w]
    
    # 显示表格ROI
    cv2.imshow('Detected Table', table_roi)
    
    cv2.imwrite("image_with_only_rectangular_contours.png", table_roi)
    
    cv2.waitKey(0)
    cv2.destroyAllWindows()
else:
    print("Error: 找不到表格")

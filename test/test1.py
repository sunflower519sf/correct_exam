import cv2
import numpy as np
import ddddocr

# 加載OCR模型
ocr = ddddocr.DdddOcr(beta=True)

# 讀取圖片
image_path = './test4_image.jpg'  # 確保這裡的路徑正確
image = cv2.imread(image_path)

# 轉換成灰階
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
# 去噪聲
blurred = cv2.GaussianBlur(gray, (5, 5), 0)
# 自適應二值化
thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                               cv2.THRESH_BINARY_INV, 11, 2)

# 使用 Canny 邊緣檢測
edges = cv2.Canny(thresh, 50, 150)
# 使用 Hough 變換檢測線條
lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100, minLineLength=100, maxLineGap=10)

# 存放水平、垂直線位置並放入圖片邊緣
height, width = image.shape[:2]
vertical_lines = [0, width]
horizontal_lines = [0, height]

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



all_img_save = []
# 根據行列數量切割圖像
for i in range(1,len(horizontal_lines)-1, 2):
    for j in range(1, len(vertical_lines)-1, 2):
        # 確定格子的邊界
        y_start = horizontal_lines[i]
        y_end = horizontal_lines[i + 1]
        x_start = vertical_lines[j]
        x_end = vertical_lines[j + 1]

        # 提取每個格子的區域
        roi = image[y_start:y_end, x_start:x_end]
        all_img_save.append(roi)

        # 將二值化圖像轉換為字節數組
        is_success, gray_bytes = cv2.imencode('.png', roi)
        if not is_success:
            raise ValueError("圖片無法編碼為 bytes 資料")
        out = ocr.classification(gray_bytes.tobytes())
        print(out)








# 顯示結果
cv2.imshow('Cut Cells', image)
cv2.waitKey(0)
cv2.destroyAllWindows()
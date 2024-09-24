import cv2
import numpy as np
import ddddocr

# 加載OCR模型
ocr = ddddocr.DdddOcr(beta=True)
ocr.set_ranges("ABCDabcdEe")


# 讀取圖片
image_path = './aimg.png'  # 確保這裡的路徑正確
image = cv2.imread(image_path)

# 轉換成灰階
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
# 去噪聲
blurred = cv2.GaussianBlur(gray, (5, 5), 0)
# 自適應二值化
thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                               cv2.THRESH_BINARY_INV, 11, 2)

# 使用 Canny 邊緣檢測
edges = cv2.Canny(thresh, 30, 200)
# 使用 Hough 變換檢測線條
min_line_length = image.shape[1] // 10  # 根據圖片大小自適應
max_line_gap = image.shape[1] // 50
lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100, minLineLength=min_line_length, maxLineGap=max_line_gap)

# 存放水平、垂直線位置並放入圖片邊緣
height, width = image.shape[:2]
vertical_lines = []
horizontal_lines = []

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
for i in range(len(horizontal_lines)-1):
    for j in range(len(vertical_lines)-1):
        # 確定格子的邊界
        y_start = horizontal_lines[i]
        y_end = horizontal_lines[i + 1]
        x_start = vertical_lines[j]
        x_end = vertical_lines[j + 1]

        # 提取每個格子的區域
        roi = image[y_start:y_end, x_start:x_end]
        all_img_save.append(roi)

        # 繪製每個格子的邊框（保留線段）
        # 繪製邊框
        cv2.rectangle(roi, (0, 0), (x_end - x_start, y_end - y_start), (0, 255, 0), 2)

        # 將每個格子保存為新圖像
        cell_image_path = f'./test/cell_{i}_{j}.png'  # 格子的文件名
        cv2.imwrite(cell_image_path, roi)


        # # 將二值化圖像轉換為字節數組
        # is_success, gray_bytes = cv2.imencode('.png', roi)
        # if not is_success:
        #     raise ValueError("圖片無法編碼為 bytes 資料")
        # out = ocr.classification(gray_bytes.tobytes(), probability=True)
        # s = ""
        # for i in out['probability']:
        #     s += out['charsets'][i.index(max(i))]
        # # print(f"{i} {j} {out}")
        # print(s)

        





# 顯示結果

cv2.imwrite('test_split.jpg', image)
cv2.imshow('Cut Cells', image)
cv2.waitKey(0)
cv2.destroyAllWindows()
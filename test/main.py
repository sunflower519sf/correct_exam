import ddddocr
import cv2
import numpy as np
import os


# 載入檢測模型
ocr_beta = ddddocr.DdddOcr(beta=True)
ocr_issu = ddddocr.DdddOcr()
# 指定範圍 減少錯誤
ocr_beta.set_ranges("ABCDabcdEe")
ocr_issu.set_ranges("ABCDabcdEe")

for filename in os.listdir("./img"):
    if not filename.split(".")[-1].lower() in ["png", "jpg", "jpeg"]:
        print(f"ERROR: {filename} 不是符合要求的圖片")
        continue

    # 讀取影像
    image = cv2.imread(filename)
    if image is None:
        print(f"ERROR: 讀取 {filename} 失敗")
        continue
    
    # 轉換成灰階圖
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # 去噪聲
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    # 自適應二質化(我也不知道 聽說這樣好像比較好辨識)
    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                    cv2.THRESH_BINARY_INV, 11, 2)

    # 找到輪廓
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # 初始化表格邊界
    table_contour = None
    max_area = 0

    # 遍歷所有輪廓找邊界
    for cnt in contours:
        approx = cv2.approxPolyDP(cnt, 0.02 * cv2.arcLength(cnt, True), True)
        if len(approx) == 4:  # 判斷是否為矩形
            area = cv2.contourArea(cnt)
            if area > max_area:
                max_area = area
                table_contour = approx

    # 提取表格取區域
    if table_contour is not None:
        x, y, w, h = cv2.boundingRect(table_contour)
        table_roi = image[y:y+h, x:x+w]
    else:
        print("Error: 找不到表格")


    # 轉換成灰階圖
    gray = cv2.cvtColor(table_roi, cv2.COLOR_BGR2GRAY)
    # 去噪聲
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    # 自適應二質化(我也不知道 聽說這樣好像比較好辨識)
    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                    cv2.THRESH_BINARY_INV, 11, 2)

    # 使用 Canny 邊緣檢測
    edges = cv2.Canny(thresh, 30, 200)
    # 使用 Hough 變換檢測線條
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=50, minLineLength=50, maxLineGap=10)

    # 存放水平、垂直線位置並放入圖片邊緣
    height, width = table_roi.shape[:2]
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

    all_ans_save = []
    for i in range(0, len(horizontal_lines)-1, 2):
        for j in range(0, len(vertical_lines)-1, 2):
            # 確定格子的邊界
            y_start = horizontal_lines[i]
            y_end = horizontal_lines[i + 1]
            x_start = vertical_lines[j]
            x_end = vertical_lines[j + 1]

            # 提取每個格子的區域
            roi = table_roi[y_start:y_end, x_start:x_end]

            # # 繪製每個格子的邊框（保留線段）
            # # 繪製邊框
            # cv2.rectangle(roi, (0, 0), (x_end - x_start, y_end - y_start), (0, 255, 0), 2)

            # 將每個格子保存為新圖像
            cell_image_path = f'./test/cell_{i}_{j}.png'  # 格子的文件名
            cv2.imwrite(cell_image_path, roi)

            
            # 將二值化圖像轉換為字節數組
            is_success, gray_bytes = cv2.imencode('.png', roi)
            if not is_success:
                raise ValueError("圖片無法編碼為 bytes 資料")
            
            out_ocr_beta = ocr_beta.classification(gray_bytes.tobytes(), probability=True)
            out_ocr_issu = ocr_issu.classification(gray_bytes.tobytes(), probability=True)
            # if out_ocr_beta == out_ocr_issu:
            #     print(out_ocr_beta)
            # else:
            #     print(f"{i}, {j} >> beta: {out_ocr_beta}, issu: {out_ocr_issu}")
            print(f"{i}, {j} >> beta: {out_ocr_beta}, issu: {out_ocr_issu}")

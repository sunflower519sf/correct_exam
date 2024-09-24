import cv2
import numpy as np

def merge_lines(lines, axis, threshold=10):
    """將線段合併到同一條線，axis=0表示垂直線，axis=1表示水平線"""
    if len(lines) == 0:
        return lines

    merged_lines = []
    lines = sorted(lines, key=lambda line: line[axis])  # 按指定軸排序
    current_line = lines[0]

    for line in lines[1:]:
        if abs(line[axis] - current_line[axis]) < threshold:  # 線段接近，合併
            current_line = [
                min(current_line[0], line[0]), min(current_line[1], line[1]),
                max(current_line[2], line[2]), max(current_line[3], line[3])
            ]
        else:
            merged_lines.append(current_line)
            current_line = line
    merged_lines.append(current_line)  # 加入最後一條線

    return merged_lines

# 讀取圖片
img = cv2.imread('test4_image.jpg')

# 將圖片轉成灰階
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# 高斯模糊去除雜訊，讓邊緣偵測更加平滑
gray = cv2.GaussianBlur(gray, (5, 5), 0)

# 用Canny進行邊緣偵測
edges = cv2.Canny(gray, 50, 150, apertureSize=3)

# 使用HoughLinesP來偵測線段
minLineLength = img.shape[1] // 10  # 根據圖片大小自適應
maxLineGap = img.shape[1] // 50
lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 100, minLineLength=minLineLength, maxLineGap=maxLineGap)

# 定義存儲垂直線和橫線的陣列
vertical_lines = []
horizontal_lines = []

# 將線條分為垂直線和橫線
if lines is not None:
    for line in lines:
        x1, y1, x2, y2 = line[0]
        
        # 檢查是否為橫線 (y座標幾乎不變)
        if abs(y2 - y1) < 10:
            horizontal_lines.append([x1, y1, x2, y2])
        
        # 檢查是否為直線 (x座標幾乎不變)
        elif abs(x2 - x1) < 10:
            vertical_lines.append([x1, y1, x2, y2])

# 整理垂直線和橫線陣列，合併相近的線段
vertical_lines = merge_lines(vertical_lines, axis=0)  # 按 x 座標整理
horizontal_lines = merge_lines(horizontal_lines, axis=1)  # 按 y 座標整理

# 繪製垂直線和橫線
for line in vertical_lines:
    x1, y1, x2, y2 = line
    cv2.line(img, (x1, y1), (x2, y2), (0, 0, 255), 2)  # 紅色垂直線

for line in horizontal_lines:
    x1, y1, x2, y2 = line
    cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 2)  # 綠色橫線

# 保存結果
cv2.imwrite('test7_final.png', img)

# 顯示結果 (如在本地環境)
# cv2.imshow('Result', img)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

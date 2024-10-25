import cv2
import numpy as np

# 讀取圖檔
img = cv2.imread('./test.png')
template = cv2.imread('./search.png')

# 圖像轉換成灰階
img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

# 框取相似圖，需定義好框的大小​，框設定與樣本圖圖片大小一致
h, w  = template.shape[:2]

# 指定匹配的方法​
method = cv2.TM_SQDIFF_NORMED

# matchTemplate()傳入待匹配圖像和模板圖像、匹配方法，得到的結果是一個單通道的float32浮點類型的圖像
res = cv2.matchTemplate(img_gray, template_gray, method)

# minMaxLoc()計算最佳匹配位置
min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res) 

# TM_SQDIFF_NORMED, 此方法要取最小值，代表最佳位置
if method in [cv2.TM_CCOEFF_NORMED, cv2.TM_SQDIFF_NORMED]:
    top_left = min_loc
else:
    top_left = max_loc

#給​rectangle框 右下的位置
bottom_right = (top_left[0] + w, top_left[1] + h)

#框取搜尋到的特徵圖​
cv2.rectangle(img,top_left, bottom_right, (0,0,255), 1)

# 顯示結果圖像
cv2.imshow('reuslt', img)
cv2.waitKey(0)
cv2.destroyAllWindows()

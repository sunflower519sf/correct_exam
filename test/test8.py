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
    thresh = cv2.adaptiveThreshold(gray, 255, 
                                cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                cv2.THRESH_BINARY_INV, 11, 2) # 二值化並反轉
    return thresh


# 載入檢測模型
ocr_beta = ddddocr.DdddOcr(beta=True)
ocr_issu = ddddocr.DdddOcr()
# 指定範圍 減少錯誤
ocr_beta.set_ranges("ABCDabcdEe")
ocr_issu.set_ranges("ABCDabcdEe")


filename = "img/aimg2.png"
# 讀取影像
image = cv2.imread(filename)
if image is None:
    print(f"ERROR: 讀取 {filename} 失敗")
    


import PIL.ImageDraw
import PIL.ImageFont
import PIL.Image

# 分數
score = "900"

# 取得圖片高度與寬度
size_height, size_width = image.shape[:2]
# 將圖片轉換為可處理格式
image = PIL.Image.fromarray(image)
# 設定字型大小及指定字體
font_size = 100
font = PIL.ImageFont.truetype('setofont.ttf', font_size, encoding='utf-8')
shear_factor = 0.5  # 設定傾斜程度


# 創建一個空白圖片用於寫入文字
text_image = PIL.Image.new("RGBA", (size_width, size_height), (0,0,0,0))
text_draw = PIL.ImageDraw.Draw(text_image)

# 設定文字位置並畫上文字(發現文字會偏移位置的話嘗試更改text_position)

text_position = (size_width-(font_size//2*len(score)), 30)
# text_position = (font_size//2, 30)
text_draw.text(text_position, score, font=font, fill=(255, 0, 0))


# 使用 shear 設定文字傾斜
text_image = text_image.transform(text_image.size, PIL.Image.AFFINE, (1, shear_factor, 0, 0, 1, 0))


# 在文字下方畫上正斜線

# 計算斜線的起點和終點位置，根據文字的位置來決定
start_point = (text_position[0], text_position[1] + font_size)  # 斜線起點 (文字左下方)
end_point = (text_position[0] + font_size * len(score), text_position[1] + font_size + 50)  # 斜線終點 (文字右下方)

# 在 text_image 上畫斜線
text_draw.line([start_point, end_point], fill=(255, 0, 0), width=5)



# 合併圖片
image.paste(text_image, (0, 0), text_image)

# draw.text(((size_width-(font_size//2)*len(score))//2, size_height//2-(font_size//2)), score, font=font, fill=(255,0,0), )

print(text_image.size)
print(image.size)
# text_image.show()
image.show()
import cv2
import numpy as np

# 影像預處理
def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) # 灰階
    thresh = cv2.adaptiveThreshold(gray, 255, 
                                cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                cv2.THRESH_BINARY_INV, 11, 2) # 二值化並反轉
    return thresh



# 加载图像，使用完整路径
img1 = cv2.imread('gg.png')  # 参考图像
img2 = cv2.imread('minus_blank.png')  # 待对齐图像

if img1 is None or img2 is None:
    print("Error: One of the images did not load. Check your file paths.")
    exit()

# 特征检测
orb = cv2.ORB_create()
keypoints1, descriptors1 = orb.detectAndCompute(img1, None)
keypoints2, descriptors2 = orb.detectAndCompute(img2, None)

# 特征匹配
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
matches = bf.match(descriptors1, descriptors2)
matches = sorted(matches, key=lambda x: x.distance)

# 输出匹配点数量
print("Number of matches:", len(matches))

if len(matches) < 4:
    print("Not enough matching points to calculate homography.")
    exit()

# 提取匹配点
src_pts = np.float32([keypoints2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)
dst_pts = np.float32([keypoints1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)

# 计算单应性矩阵
H, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC)

# 应用透视变换
height, width, _ = img1.shape
aligned_img2 = cv2.warpPerspective(img2, H, (width, height))


preprocess_img1 = preprocess_image(img1)
preprocess_img2 = preprocess_image(aligned_img2)

use_image_blank = cv2.absdiff(preprocess_img1, preprocess_img2) 


# 显示结果
cv2.imwrite('out.png', use_image_blank)


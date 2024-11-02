import cv2
import numpy as np

# 第一步：加载图像
img1 = cv2.imread('gg.png')  # 主图像
img2 = cv2.imread('minus_blank.png')  # 待对齐图像

# 第二步：检测特征点
orb = cv2.ORB_create()
keypoints1, descriptors1 = orb.detectAndCompute(img1, None)
keypoints2, descriptors2 = orb.detectAndCompute(img2, None)

# 第三步：特征匹配
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
matches = bf.match(descriptors1, descriptors2)
matches = sorted(matches, key=lambda x: x.distance)

# 第四步：提取匹配点
src_pts = np.float32([keypoints2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)
dst_pts = np.float32([keypoints1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)

# 计算单应性矩阵
H, _ = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC)

# 获取主图像的大小
height, width, _ = img1.shape

# 创建一个白色背景
white_background = np.ones((height, width, 3), dtype=np.uint8) * 255

# 将第二张图像应用透视变换
aligned_img2 = cv2.warpPerspective(img2, H, (width, height))

# 将对齐后的图像放置到白色背景上的对应位置
# 假设第二张图像是需要的部分，直接将其放到背景上
mask = aligned_img2[:, :, 0] > 0  # 根据需要调整掩码条件
white_background[mask] = aligned_img2[mask]

# 显示结果
cv2.imwrite('out.png', white_background)
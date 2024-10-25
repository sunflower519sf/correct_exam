# import the necessary pages
from imutils.object_detection import non_max_suppression
import numpy as np
import argparse
import cv2

# 載入圖片
image = cv2.imread("test.png")
template = cv2.imread("src/img/template.png")
(tH, tW) = template.shape[:2]  # 取得模板的大小

# # display the  image and template to our screen
# cv2.imshow("Image", image)
# cv2.imshow("Template", template)
# cv2.waitKey(0)

imageGray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
templateGray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

cv2.imshow("ImageGray", imageGray)
cv2.waitKey(0)
# 執行模板匹配
print("[INFO] performing template matching...")
result = cv2.matchTemplate(imageGray, templateGray,
	cv2.TM_CCOEFF_NORMED)

# find all locations in the result map where the matched value is
# greater than the threshold, then clone our original image so we
# can draw on it
(yCoords, xCoords) = np.where(result >= 0.8)
clone = image.copy()
print("[INFO] {} matched locations *before* NMS".format(len(yCoords)))

# loop over our starting (x, y)-coordinates
for (x, y) in zip(xCoords, yCoords):
	# draw the bounding box on the image
	cv2.rectangle(clone, (x, y), (x + tW, y + tH),
		(255, 0, 0), 3)

# # show our output image *before* applying non-maxima suppression
# cv2.imshow("Before NMS", clone)
# cv2.waitKey(0)

# initialize our list of rectangles
rects = []

# loop over the starting (x, y)-coordinates again
for (x, y) in zip(xCoords, yCoords):
	# update our list of rectangles
	rects.append((x, y, x + tW, y + tH))

# apply non-maxima suppression to the rectangles
pick = non_max_suppression(np.array(rects))
print("[INFO] {} matched locations *after* NMS".format(len(pick)))

# loop over the final bounding boxes
for (startX, startY, endX, endY) in pick:
	# draw the bounding box on the image
	cv2.rectangle(image, (startX, startY), (endX, endY),
		(255, 0, 0), 3)

# show the output image
cv2.imshow("After NMS", image)
cv2.waitKey(0)

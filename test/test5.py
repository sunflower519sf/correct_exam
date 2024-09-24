import cv2
import numpy as np

img = cv2.imread('test4_image.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(gray, (5, 5), 0)
edges = cv2.Canny(blurred, 100, 150, apertureSize=3)

minLineLength =2
maxLineGap = 4
lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 100, minLineLength, maxLineGap, 10)
print(lines)
# tody_lines_list = np.array(lines, dtype=np.float32).reshape(len(lines), 2, 2)
# print(tody_lines_list)
points = np.array(lines, dtype=np.float32).reshape(len(lines), 2, 2)



# for line in lines:
#     for x1, y1, x2, y2 in line:
#         cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 2)

# cv2.imwrite('houghlines5.jpg', img)
# cv2.imshow("image", edges)
# cv2.imshow('img', img)
# cv2.waitKey(0)



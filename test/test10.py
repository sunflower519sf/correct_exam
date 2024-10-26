import cv2



img = cv2.imread("test.png")

# # 修改大小
# img = cv2.resize(img, (600, 650))  # 將大小修改成600*650

# # 儲存圖片
# cv2.imwrite('test1.jpg', img)

x, y, w, h = 7,688,40,50
test = img[y:y+h, x:x+w]
cv2.imwrite("aaa.png", test)


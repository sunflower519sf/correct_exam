import os
import cv2
import numpy as np
import re
from csvreadwrite import read_csv, write_csv
import yaml
from imutils.object_detection import non_max_suppression

# 計算兩點距離
def calculate_the_distance_between_2_points(points1, points2):
    return ((points2[0] - points1[0]) ** 2 + (points2[1] - points1[1]) ** 2) ** 0.5

# 計算兩點中點座標
def calculate_the_center_point_of_2_points(points):
    return [(points[0] + points[2])/2, (points[1] + points[3])/2]

# 影像預處理
def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) # 灰階
    thresh = cv2.adaptiveThreshold(gray, 255, 
                                cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                cv2.THRESH_BINARY_INV, 11, 2) # 二值化並反轉
    return thresh

# 檔案或路徑名稱防呆
def safe_filename(name:str):
    return name.replace("\\", "/").strip(".").strip("/")

# 陣列文字大小寫統一
def safe_text(lst:list):
    return [char.lower() for char in lst]

# 字串處理
def safe_string(string:str):
    return re.sub(r"[^a-zA-Z0-9]+", "", string).lower()

# 取得答案檔
def get_ans_file(all_img_file:list, CONFIG):
    global ans_file_name
    # 取得檔案名稱
    file_name = safe_filename(CONFIG["img"]["ans_file_name"])
    
    
    if file_name.split(".")[-1].lower() in safe_text(CONFIG["img"]["format"]):
        if file_name in all_img_file:
            ans_file_name = file_name
            all_img_file.remove(file_name)
            return [f"{file_name}/ansfile?.ansfile?"] + all_img_file
        else:
            return ["nofile?.ansfile?"] + all_img_file
    else:
        for file_extension in safe_text(CONFIG["img"]["format"]):
            file_name = f"{file_name}.{file_extension}" 
            if file_name in all_img_file:
                ans_file_name = file_name
                all_img_file.remove(file_name)
                return [f"{file_name}/ansfile?.ansfile?"] + all_img_file
        else:
            return ["nofile?.ansfile?"] + all_img_file



# 載入配置文件
with open("config.yaml", "r", encoding="utf-8") as fr:
    CONFIG = yaml.safe_load(fr)

# 載入定位圖片
template = cv2.imread(safe_filename(CONFIG["img"]["template_file"]))

# 確保有此資料夾
folder_path = safe_filename(CONFIG["img"]["folder_path"])
if not os.path.exists(folder_path):
    os.makedirs(folder_path)
    print(f"ERROR: 查無此資料夾 以自動建立資料夾 {CONFIG['img']['folder_path']}")


# 確保有答案
have_ans = False
# 使用for提取資料夾中所有圖片
for filename in get_ans_file(os.listdir(folder_path), CONFIG):
    filename = safe_filename(filename)
    print(filename)
    # 檢測是否符合格式 增加一個條件用於檢測答案檔
    check_is_ans_file = False

    # 判斷是否為答案檔案
    check_file_name = filename.split(".")[-1].lower() 
    if check_file_name == "ansfile?":
        ans_file_split = filename.split("/")
        if ans_file_split[-1] == "ansfile?.ansfile?":
            filename = ans_file_split[0]
            check_is_ans_file = True
        elif ans_file_split[-1] == "nofile?.ansfile?":
            print(f"ERROR: 找不到指定的答案檔案")
            continue
    elif not check_file_name in safe_text(CONFIG["img"]["format"]):
        print(f"ERROR: {filename} 不是符合要求的圖片格式 以下是可接受的格式:\n{', '.join(CONFIG['img']['format'])}")
        continue

    # 讀取影像
    image = cv2.imread(f"{safe_filename(CONFIG['img']['folder_path'])}/{filename}")
    if image is None:
        print(f"ERROR: 讀取 {filename} 失敗")
        continue

    # 影像預處理
    thresh = preprocess_image(image)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # 過濾輪廓並找出矩形 並指定最大值
    max_area = 0
    contour_with_max_area = None
    for contour in contours:
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
        if len(approx) == 4:
            area = cv2.contourArea(contour)
            if area > max_area:
                max_area = area
                contour_with_max_area = approx
    if contour_with_max_area is None:
        print(f"Error: {filename} 找不到有效的矩形")
        continue
    
    # 使用透視變換切割圖片
    if CONFIG["find_table"]["auto_perspective"]:
        # 重塑矩形
        sorting_pos_pts = np.array(contour_with_max_area).reshape(4, 2)
        # 建立一個存放最後結果的矩形
        contour_with_max_area_ordered = np.zeros((4, 2), dtype="float32")

        # 找出左上角和右下角
        sorting_pos_s = [sum(i) for i in sorting_pos_pts]
        contour_with_max_area_ordered[0] = sorting_pos_pts[np.argmin(sorting_pos_s)]
        contour_with_max_area_ordered[2] = sorting_pos_pts[np.argmax(sorting_pos_s)]

        # 找出右上角和左下角
        sorting_pos_diff = np.diff(sorting_pos_pts, axis=1)
        contour_with_max_area_ordered[1] = sorting_pos_pts[np.argmin(sorting_pos_diff)]
        contour_with_max_area_ordered[3] = sorting_pos_pts[np.argmax(sorting_pos_diff)]
        
        # 取得圖像寬度
        existing_image_width = image.shape[1]

        # 計算左上角到右上角的距離
        distance_between_top_left_and_top_right = calculate_the_distance_between_2_points(contour_with_max_area_ordered[0], contour_with_max_area_ordered[1])
        # 計算左上角到左下角的距離
        distance_between_top_left_and_bottom_left = calculate_the_distance_between_2_points(contour_with_max_area_ordered[0], contour_with_max_area_ordered[3])

        # 計算長寬比
        aspect_ratio = distance_between_top_left_and_bottom_left / distance_between_top_left_and_top_right
        
        # 設定新圖像的長寬
        new_image_width = existing_image_width
        new_image_height = int(new_image_width * aspect_ratio)

        # 透視變換
        perspective_transform_pts1 = np.float32(contour_with_max_area_ordered)
        perspective_transform_pts2 = np.float32([[0, 0], [new_image_width, 0], [new_image_width, new_image_height], [0, new_image_height]])
        # 計算透視變換矩陣(好像是把pts1映射到pts2)
        perspective_transform_matrix = cv2.getPerspectiveTransform(perspective_transform_pts1, perspective_transform_pts2)
        # 將它應用到圖像上 perspective_transformed_image就是表格了
        use_image = cv2.warpPerspective(image, perspective_transform_matrix, (new_image_width, new_image_height))

    # 直接檢測方格裁切
    else:
        x, y, w, h = cv2.boundingRect(contour_with_max_area)
        use_image = image[y:y+h, x:x+w]
    # 將圖片調整為指定大小
    use_image = cv2.resize(use_image, (CONFIG["find_table"]["crop_ratio_mult"]*12, CONFIG["find_table"]["crop_ratio_mult"]*13)) # 大概是12:13的比例


    # 尋找出定位點
    # 預處理圖片
    use_image_preprocess = preprocess_image(use_image)
    template_preprocess = preprocess_image(template)

    # 計算匹配值 
    result = cv2.matchTemplate(use_image_preprocess, template_preprocess,
	cv2.TM_CCOEFF_NORMED)
    # 找出匹配值高於設定值的部分
    (yCoords, xCoords) = np.where(result >= CONFIG["find_table"]["position_image_domain_value"])
    # 取得模板大小
    template_tH, template_tW = template.shape[:2]
    # 構建所需執行矩形
    template_rects = [(x, y, x + template_tW, y + template_tH) for (x, y) in zip(xCoords, yCoords)]
    # 對矩形應用非極大值抑制(即為定位點的座標)
    template_pick = non_max_suppression(np.array(template_rects))
    # 計算定位點的中心點
    position_points = [calculate_the_center_point_of_2_points(rect) for rect in template_pick]
    
    # 每個格子高度55 寬度46(設定乘數分別乘上 0.55:0.46)
    clone = use_image.copy()
    for position in position_points:
        # 計算格子座標
        for number in range(CONFIG["find_table"]["number_of_rows"]):
            pos_y = position[1] + (number+1) * (0.55*CONFIG["find_table"]["crop_ratio_mult"])
            for option in range(CONFIG["find_table"]["number_of_answers"]):
                pos_x = position[0] + (option+1) * (0.46*CONFIG["find_table"]["crop_ratio_mult"])
                
                # 將每個點畫出來
                
                clone = cv2.rectangle(clone, (int(pos_x)-5, int(pos_y)-5), (int(pos_x)+5, int(pos_y)+5), (0, 0, 255), 2)
                cv2.imwrite("output.png", clone)
        



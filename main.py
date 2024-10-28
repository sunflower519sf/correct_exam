import os
import cv2
import numpy as np
import re
from csvreadwrite import read_csv, write_csv
import yaml
from imutils.object_detection import non_max_suppression
import time


# 計算兩點距離
def calculate_the_distance_between_2_points(points1, points2):
    return ((points2[0] - points1[0]) ** 2 + (points2[1] - points1[1]) ** 2) ** 0.5

# 計算兩點中點座標
def calculate_the_center_point_of_2_points(points):
    return [(points[0] + points[2])/2, (points[1] + points[3])/2]

# 讀取圖片檔案
def read_image_file(filename):
    return cv2.imdecode(np.fromfile(filename,dtype=np.uint8),-1)

# 影像預處理
def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) # 灰階
    thresh = cv2.adaptiveThreshold(gray, 255, 
                                cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                cv2.THRESH_BINARY_INV, 11, 2) # 二值化並反轉
    return thresh

# 計算匹配並回傳
def match_template(old_image, template_image, CONFIG):
    result = cv2.matchTemplate(old_image, template_image,
	cv2.TM_CCOEFF_NORMED)
    # 找出匹配值高於設定值的部分
    (yCoords, xCoords) = np.where(result >= CONFIG["find_table"]["position_image_domain_value"])
    # 取得模板大小
    template_tH, template_tW = template_image.shape[:2]
    # 構建所需執行矩形
    template_rects = [(x, y, x + template_tW, y + template_tH) for (x, y) in zip(xCoords, yCoords)]
    # 對矩形應用非極大值抑制(即為定位點的座標)
    template_pick = non_max_suppression(np.array(template_rects))
    # 計算定位點的中心點
    position_points = [calculate_the_center_point_of_2_points(rect) for rect in template_pick]
    return position_points


# 檔案或路徑名稱防呆
def safe_filename(name:str):
    return name.replace("\\", "/").strip(".").strip("/")

# 陣列文字大小寫統一
def safe_text(lst:list):
    return [char.lower() for char in lst]

# 字串處理
def safe_string(string:str):
    return re.sub(r"[^a-zA-Z0-9]+", "", string).lower()

# 防止座標超出
def safe_coordinate(pos):
    return 0 if pos < 0 else pos

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

# 載入答案定位圖片
template = read_image_file(safe_filename(f'{CONFIG["img"]["contrast_folder"]}/{CONFIG["img"]["ans_template_file"]}'))
# 載入空白答案卡
minus_blank = read_image_file(safe_filename(f'{CONFIG["img"]["contrast_folder"]}/{CONFIG["img"]["minus_blank_file"]}'))
# 載入座號定位圖片
number_template = read_image_file(safe_filename(f'{CONFIG["img"]["contrast_folder"]}/{CONFIG["img"]["number_template_file"]}'))

# 確保有此資料夾
folder_path = safe_filename(CONFIG["img"]["folder_path"])
if not os.path.exists(folder_path):
    os.makedirs(folder_path)
    print(f"ERROR: 查無此資料夾 以自動建立資料夾 {CONFIG['img']['folder_path']}")


# 確保有答案
have_ans = []
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
    image = read_image_file(f"{safe_filename(CONFIG['img']['folder_path'])}/{filename}")
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

    # 儲存空白用
    # cv2.imwrite("minus_blank.png", use_image)

    # 尋找出定位點
    # 預處理圖片
    use_image_preprocess = preprocess_image(use_image) # 裁切後的原始圖片
    minus_blank_preprocess = preprocess_image(minus_blank) # 空白答案卡
    template_preprocess = preprocess_image(template) # 答案定位模板
    number_template_preprocess = preprocess_image(number_template) # 座號定位模板
    # 將原有答案卡部分清除 只保留劃記痕跡
    use_image_blank = cv2.subtract(use_image_preprocess, minus_blank_preprocess) 
    
    # 取得答案
    # 計算匹配值
    position_points = match_template(use_image_preprocess, template_preprocess, CONFIG)
    # 存放答案用陣列
    all_ans_out = []
    ct = 0
    for position in sorted(position_points):
        # 計算格子座標
        ans_number_selected = []
        for number in range(CONFIG["find_table"]["number_of_rows"]):
            pos_y = position[1] + (number+1) * (0.54*CONFIG["find_table"]["crop_ratio_mult"]) + (number+1) * (0.008*CONFIG["find_table"]["crop_ratio_mult"])
            ans_selected_option = []
            for option in range(CONFIG["find_table"]["number_of_answers"]):
                pos_x = position[0] + (option+1) * (0.43*CONFIG["find_table"]["crop_ratio_mult"]) + (option) * (0.045*CONFIG["find_table"]["crop_ratio_mult"])
                
                # 取得答案
                get_ans_img = use_image_blank[int(pos_y)-22:int(pos_y)+22, int(pos_x)-18:int(pos_x)+18]
                
                # 將圖片中內容放大
                ans_img_dilated = cv2.dilate(get_ans_img, None, iterations=CONFIG["find_table"]["option_detect_expansion_degree"])
                
                # 計算像素點數量
                total_pixels = ans_img_dilated.size
                # 計算白色像素點數量
                white_pixels = np.sum(ans_img_dilated > 200)
                # 計算比率
                white_pixel_ratio = white_pixels/total_pixels*100
                if white_pixel_ratio > CONFIG["find_table"]["option_detect_domain_value"]:
                    ans_selected_option.append(True)
                else:
                    ans_selected_option.append(False)
            ans_number_selected.append(ans_selected_option)
        all_ans_out.append(ans_number_selected)
        ct += 1
    
    # 讀取座號
    # 計算匹配值 
    position_points_number = sorted(match_template(use_image_preprocess, number_template_preprocess, CONFIG), key=lambda x: x[1])[1:]
    
    # 計算座號
    seat_number = ["", ""]
    if len(position_points_number) == 2:
        for posnum in range(2):
            position = position_points_number[posnum]
            pos_y = position[1]
            for num in range(10):
                pos_x = position[0] - (4.92*CONFIG["find_table"]["crop_ratio_mult"]) + (num) * (0.49*CONFIG["find_table"]["crop_ratio_mult"]) + (num) * (0.001*CONFIG["find_table"]["crop_ratio_mult"])
                # 取得座號
                get_number_img = use_image_blank[int(pos_y)-25:int(pos_y)+25, int(pos_x)-20:int(pos_x)+20]
                # 將座號放大
                number_img_dilated = cv2.dilate(get_number_img, None, iterations=CONFIG["find_table"]["option_detect_expansion_degree"])
                # 計算像素點數量
                total_pixels = number_img_dilated.size
                # 計算白色像素點數量
                white_pixels = np.sum(number_img_dilated > 200)
                # 計算比率
                white_pixel_ratio = white_pixels/total_pixels*100
                if white_pixel_ratio > CONFIG["find_table"]["option_detect_domain_value"]:
                    seat_number[posnum] += str(num)
        # 格式化座號
        image_number = "".join(seat_number)
    else:
        # 無座號直接使用檔案名稱
        image_number = filename
    
    # 如果是答案就存起來
    if check_is_ans_file: 
        have_ans = all_ans_out.copy()
        save_data = ["ans", all_ans_out, 100]
        write_csv(safe_filename(CONFIG['img']['ans_file_name']), filename, save_data)
        print(f"已找到答案檔案 {filename} 並用於評分")
        continue

    # 確認是否有答案
    if len(have_ans) <= 0:
        # 儲存答案
        save_data = [image_number, all_ans_out, 100]
        write_csv(safe_filename(CONFIG['img']['ans_file_name']), filename, save_data)
    # 有答案
    else:
        # have_ans all_ans_out
        # 計算分數
        score = 0
        one_question_score = CONFIG["score_setting"]["total_score"]/CONFIG["score_setting"]["number_of_questions"]
        for column in range(len(all_ans_out)):
            for row in range(CONFIG["find_table"]["number_of_rows"]):
                if (column*CONFIG["find_table"]["number_of_rows"]+row) > CONFIG["score_setting"]["number_of_questions"]:break
                if have_ans[column][row] == all_ans_out[column][row]:
                    score += one_question_score
        # 儲存答案
        save_data = [image_number, all_ans_out, score]
        write_csv(safe_filename(CONFIG['img']['ans_file_name']), filename, save_data)


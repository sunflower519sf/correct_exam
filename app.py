import ddddocr
import os
import cv2
import numpy as np
import json
import re
from csvreadwrite import read_csv, write_csv

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
def get_ans_file(all_img_file:list, config):
    # 取得路徑
    file_path = safe_filename(config["img"]["folder_path"])
    # 取得檔案名稱
    file_name = safe_filename(config["img"]["ans_file_name"])
    
    
    if file_name.split(".")[-1].lower() in safe_text(config["img"]["format"]):
        if file_name in all_img_file:
            return [f"{file_name}/ansfile?.ansfile?"] + all_img_file.remove(file_name)
        else:
            return ["nofile?.ansfile?"] + all_img_file
    else:
        for file_extension in safe_text(config["img"]["format"]):
            file_name = f"{file_name}.{file_extension}" 
            if file_name in all_img_file:
                return [f"{file_name}/ansfile?.ansfile?"] + all_img_file.remove(file_name)
        else:
            return ["nofile?.ansfile?"] + all_img_file
        
    
    

# 載入配置文件
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)


# 載入檢測模型
ocr_beta = ddddocr.DdddOcr(beta=True)
ocr_issu = ddddocr.DdddOcr()
# 指定範圍 減少錯誤
ocr_beta.set_ranges("ABCDabcdEe")
ocr_issu.set_ranges("ABCDabcdEe")


# 用於臨時存放答案
eaxm_ans_dict = {}

# 確保有此資料夾
folder_path = safe_filename(config["img"]["folder_path"])
if not os.path.exists(folder_path):
    os.makedirs(folder_path)
    print(f"ERROR: 查無此資料夾 以自動建立資料夾 {config['img']['folder_path']}")
# 確保有答案
have_ans = False
# 使用for提取資料夾中所有圖片
for filename in get_ans_file(os.listdir(folder_path), config):
    filename = safe_filename(filename)
    print(filename)
    # 檢測是否符合格式 增加一個條件用於檢測答案檔
    check_is_ans_file = False
    
    check_file_name = filename.split(".")[-1].lower() 
    if check_file_name == "ansfile?":
        ans_file_split = filename.split("/")
        if ans_file_split[-1] == "ansfile?.ansfile?":
            filename = ans_file_split[0]
            check_is_ans_file = True
        elif ans_file_split[-1] == "nofile?.ansfile?":
            print(f"ERROR: 找不到指定的答案檔案")
            continue
    elif not check_file_name in safe_text(config["img"]["format"]):
        print(f"ERROR: {filename} 不是符合要求的圖片格式 以下是可接受的格式:\n{', '.join(config['img']['format'])}")
        continue
    
    


    # 讀取影像
    image = cv2.imread(f"{safe_filename(config['img']['folder_path'])}/{filename}")
    
    if image is None:
        print(f"ERROR: 讀取 {filename} 失敗")
        continue

    # 影像預處理
    thresh = preprocess_image(image)
    
    # 膨脹 
    dilated_image = cv2.dilate(thresh, None, iterations=config["find_table"]["line_expansion_degree"])

    # 找出輪廓
    contours, hierarchy = cv2.findContours(dilated_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    # 過濾輪廓並找出矩形
    rectangular_contours = []
    for contour in contours:
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
        if len(approx) == 4:
            rectangular_contours.append(approx)

    # 找出最大輪廓
    max_area = 0
    contour_with_max_area = None
    for contour in rectangular_contours:
        area = cv2.contourArea(contour)
        if area > max_area:
            max_area = area
            contour_with_max_area = contour
    if contour_with_max_area is None:
        print(f"Error: {filename} 找不到有效的矩形")
        continue

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

    # 將寬度縮小
    existing_image_width_reduced_by_10_percent = int(existing_image_width * 0.9)

    # 計算左上角到右上角的距離
    distance_between_top_left_and_top_right = calculate_the_distance_between_2_points(contour_with_max_area_ordered[0], contour_with_max_area_ordered[1])
    # 計算左上角到左下角的距離
    distance_between_top_left_and_bottom_left = calculate_the_distance_between_2_points(contour_with_max_area_ordered[0], contour_with_max_area_ordered[3])

    # 計算長寬比
    aspect_ratio = distance_between_top_left_and_bottom_left / distance_between_top_left_and_top_right

    # 設定新圖像的長寬
    new_image_width = existing_image_width_reduced_by_10_percent
    new_image_height = int(new_image_width * aspect_ratio)

    # 透視變換
    perspective_transform_pts1 = np.float32(contour_with_max_area_ordered)
    perspective_transform_pts2 = np.float32([[0, 0], [new_image_width, 0], [new_image_width, new_image_height], [0, new_image_height]])
    # 計算透視變換矩陣(好像是把pts1映射到pts2)
    perspective_transform_matrix = cv2.getPerspectiveTransform(perspective_transform_pts1, perspective_transform_pts2)
    # 將它應用到圖像上 perspective_transformed_image就是表格了
    perspective_corrected_image = cv2.warpPerspective(image, perspective_transform_matrix, (new_image_width, new_image_height))

    # 將圖片周圍填充白色
    # 取得圖像高度
    image_height = image.shape[0]
    # 計算填充的大小
    padding = int(image_height * 0.1)
    # 填充圖像
    perspective_corrected_image_with_padding = cv2.copyMakeBorder(perspective_corrected_image, padding, padding, padding, padding, cv2.BORDER_CONSTANT, value=[255, 255, 255])


    
    sorting_pos_pts = np.array(contour_with_max_area).reshape((4, 2))
    # 建立一個矩形 其中都是0 
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

    # 將寬度縮小
    existing_image_width_reduced_by_10_percent = int(existing_image_width * 0.9)

    # 計算左上角到右上角的距離
    distance_between_top_left_and_top_right = calculate_the_distance_between_2_points(contour_with_max_area_ordered[0], contour_with_max_area_ordered[1])
    # 計算左上角到左下角的距離
    distance_between_top_left_and_bottom_left = calculate_the_distance_between_2_points(contour_with_max_area_ordered[0], contour_with_max_area_ordered[3])

    # 計算長寬比
    aspect_ratio = distance_between_top_left_and_bottom_left / distance_between_top_left_and_top_right

    # 設定新圖像的長寬
    new_image_width = existing_image_width_reduced_by_10_percent
    new_image_height = int(new_image_width * aspect_ratio)

    # 透視變換
    perspective_transform_pts1 = np.float32(contour_with_max_area_ordered)
    perspective_transform_pts2 = np.float32([[0, 0], [new_image_width, 0], [new_image_width, new_image_height], [0, new_image_height]])
    # 計算透視變換矩陣(好像是把pts1映射到pts2)
    perspective_transform_matrix = cv2.getPerspectiveTransform(perspective_transform_pts1, perspective_transform_pts2)
    # 將它應用到圖像上 perspective_transformed_image就是表格了
    perspective_corrected_image = cv2.warpPerspective(image, perspective_transform_matrix, (new_image_width, new_image_height))

    # 將圖片周圍填充白色
    # 取得圖像高度
    image_height = image.shape[0]
    # 計算填充的大小
    padding = int(image_height * 0.1)
    # 填充圖像
    perspective_corrected_image_with_padding = cv2.copyMakeBorder(perspective_corrected_image, padding, padding, padding, padding, cv2.BORDER_CONSTANT, value=[255, 255, 255])

    # 影像預處理
    thresh = preprocess_image(perspective_corrected_image_with_padding)

    # 使用 Canny 邊緣檢測
    edges = cv2.Canny(thresh, 30, 200)
    # 使用 Hough 變換檢測線條
    min_line_length = perspective_corrected_image_with_padding.shape[1] // 10  # 根據圖片大小自適應
    max_line_gap = perspective_corrected_image_with_padding.shape[1] // 50
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100, minLineLength=min_line_length, maxLineGap=max_line_gap)

    # 存放水平、垂直線位置
    horizontal_lines = []
    vertical_lines = []

    # 處理檢測到的線條
    for line in lines:
        x1, y1, x2, y2 = line[0]
        if abs(y2 - y1) < 10:  # 水平直線
            horizontal_lines.append(y1)
        elif abs(x2 - x1) < 10:  # 垂直直線
            vertical_lines.append(x1)

    # 去重並排序線條位置
    horizontal_lines = sorted(list(set(horizontal_lines)))
    vertical_lines = sorted(list(set(vertical_lines)))

    # 定義檢測用的資料
    # 設定水平、垂直線的間隔
    horizontal_line_spacing = perspective_corrected_image.shape[0] / len(horizontal_lines)
    vertical_line_spacing = perspective_corrected_image.shape[1] / len(vertical_lines)
    
    # 根據行列數量切割圖像
    all_img_save = []
    for i in range(len(horizontal_lines)-1):
        temp_img_save = []
        have_data = False
        for j in range(len(vertical_lines)-1):
            # 確定格子的邊界
            y_start = horizontal_lines[i]
            y_end = horizontal_lines[i + 1]
            x_start = vertical_lines[j]
            x_end = vertical_lines[j + 1]

            # 提取每個格子的區域
            roi = perspective_corrected_image_with_padding[y_start:y_end, x_start:x_end]
            
            # 儲存符合大小的影像
            if abs(y_end-y_start) > horizontal_line_spacing and abs(x_end-x_start) > vertical_line_spacing:
                temp_img_save.append(roi)
                have_data = True
        if have_data:
            all_img_save.append(temp_img_save)

    # 逐一檢測每個格子的文字
    save_ans_all = []
    for line_img in all_img_save:
        save_ans_temp = []
        for img in line_img:
            # 影像預處理
            img_orc = preprocess_image(img)
            
            # 這裡可以用其他模型檢查答案
            # 將二值化圖像轉換為字節數組
            is_success, gray_bytes = cv2.imencode('.png', img_orc)
            if not is_success:
                raise ValueError("圖片無法編碼為 bytes 資料")
            
            # 使用不同模型檢查答案
            result_beta = ocr_beta.classification(gray_bytes.tobytes())
            result_issu = ocr_issu.classification(gray_bytes.tobytes())

            print(f"Beta: {result_beta}\nIssu: {result_issu}")
            # 儲存答案
            save_ans = [f"{safe_string(result_beta)}", f"{safe_string(result_issu)}"]
            save_ans_temp.append(save_ans)
        save_ans_all.append(save_ans_temp)

    if check_is_ans_file:
        eaxm_ans_dict[filename] = save_ans_all.copy()
        write_csv(config["read_write_csv"]["data_delimiter"], filename, [save_ans_all.copy(), 100])
        have_ans = True
        print("提示: 答案已取得 存入檔案")
        continue
   
    else:
        # 計算分數
        score = 0
        if not have_ans:
            print("提示: 沒有答案, 無法取得分數")
        
        else:
            answer_data = eaxm_ans_dict[safe_filename(config["img"]["ans_file_name"])]
            for line in range(len(answer_data)):
                for value in range(len(answer_data[line])):
                    if len(eaxm_ans_dict[filename]) > line and len(eaxm_ans_dict[filename][line]) > value:
                        for data in range(len(answer_data[line][value])):
                            if len(eaxm_ans_dict[filename][line][value]) > data:
                                if answer_data[line][value][data] == eaxm_ans_dict[filename][line][value][data]:
                                    score += config["score_setting"]["score_per_question"]
                            else:
                                print(f"Error: 答案超出範圍 請確認 {config['read_write_csv']['csv_file_name']} 中的答案是否有多餘的資料")
                    else:
                        print(f"Error: 答案超出範圍 請確認 {config['read_write_csv']['csv_file_name']} 中的答案是否有多餘的資料")
            print(f"分數: {score}")
        write_csv(config["read_write_csv"]["data_delimiter"], filename, [save_ans_all.copy(), score])
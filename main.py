import os
import cv2
import numpy as np
from imutils.object_detection import non_max_suppression
import math
import re
import yaml
import ast
import time
from datetime import datetime
import gradio as gr
import hashlib
from pypdf import PdfReader
# from fitz import Document, Pixmap


# 計算兩點距離
def calculate_the_distance_between_2_points(points1, points2):
    return ((points2[0] - points1[0]) ** 2 + (points2[1] - points1[1]) ** 2) ** 0.5

# 計算兩點中點座標
def calculate_the_center_point_of_2_points(points):
    return [(points[0] + points[2])/2, (points[1] + points[3])/2]

# 回傳錯誤訊息
def error_message(message, check_error=""):
    global CONFIG
    if CONFIG["img"]["interface"]:
        if check_error == "error":
            raise gr.Error("請上傳檔案", title="錯誤")
        elif check_error == "warning":
            gr.Warning(message, title="警告")
        else:
            gr.Info(message, title="提示")
        
    else:
        print(f"ERROR: {message}")
    return

# 讀取圖片檔案
def read_image_file(filename):
    return cv2.imdecode(np.fromfile(filename,dtype=np.uint8),-1)

def log_safe_filename(name:str):
    out = name.replace("\\", "/").strip("/").replace(".log", "")
    log_time = datetime.now().strftime("%Y-%m-%d")
    out_path = out.replace("%name%", log_time)
    return f'{out_path}.log'

## 記錄檔使用
# 讀取記錄檔
def read_csv(filename):
    global CONFIG
    filename = log_safe_filename(filename)
    lst = {}
    with open(f'{filename}', 'r', encoding='utf-8') as csvfile:
        linedata = csvfile.readlines()
        for i in linedata:
            data = i.strip().split(CONFIG["read_write_log"]["data_delimiter"])
            # lst[data[0]] = eval(data[1]) 
            lst[data[0]] = ast.literal_eval(data[1])
    return lst

# def write_dict_csv(filename, lst:dict):
#     global CONFIG
#     filename = safe_filename(filename)
#     with open(f'{filename}', 'w', encoding='utf-8') as csvfile:
#         for i in lst:
#             csvfile.write(f'{i}{CONFIG["read_write_log"]["data_delimiter"]}')
#             csvfile.write(str(lst[i]))
#             csvfile.write("\n")

# 寫入記錄檔
def write_csv(filename, keyname, value):
    global CONFIG
    filename = log_safe_filename(filename)
    with open(f'{filename}', 'a', encoding='utf-8') as csvfile:
        csvfile.write(f'{keyname}{CONFIG["read_write_log"]["data_delimiter"]}{str(value)}\n')
##

# 影像預處理
def preprocess_image(image):
    gray = image if len(image.shape) == 2 else cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) # 灰階
    # 高斯模糊
    blurred_image = cv2.GaussianBlur(gray, (11, 11), 0)
    # 使用二值化
    preprocessing_dualization = int(CONFIG["find_table"]["preprocessing_dualization"])
    if preprocessing_dualization >= 255:
        preprocessing_dualization = 255
    elif preprocessing_dualization <= 0:
        preprocessing_dualization = 0
    _, binary_image = cv2.threshold(blurred_image, preprocessing_dualization, 255, cv2.THRESH_BINARY)
    # 反轉圖片（黑色變白色，白色變黑色）
    inverted_image = cv2.bitwise_not(binary_image)
    return inverted_image

# 計算匹配並回傳
def match_template(old_image, template_image, CONFIG):
    old_image = cv2.dilate(old_image, None, iterations=1)
    template_image = cv2.dilate(template_image, None, iterations=1)
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

# 匯出檔案名稱防呆
def safe_filename_export(name:str):
    out = name.replace("\\", "/").strip("/")
    return f'{out}/{datetime.now().strftime("%Y_%m_%d_%Hh%Mm%Ss")}.csv'

# 陣列文字大小寫統一
def safe_text(lst:list):
    return [char.lower() for char in lst]

# 格式化座號
def format_number(number):
    number = str(number).replace(" ", "").zfill(2)
    if number == "": return "00"
    return number

# 檢查字典
def check_dict(data, key):
    if key not in data: return False, key
    count = 1
    temp_key = key
    while temp_key in data:
        temp_key = f"{key}_{count}"
        count += 1
    return True, temp_key

# 轉換為字母
def convert_alphabet(data):
    """
    字母對照(參考考選部https://wwwc.moex.gov.tw/main/content/wHandMenuFile.ashx?file_id=404)
    A:A, B:B, C:C, D:D,
    F:AB, G:AC, H:AD,
    J:BC, K:BD, M:CD,
    P:ABC, Q:ABD, S:ACD
    V:BCD, Z:ABCD, 未作答:=
    """
    if type(data) == list:
        if data == [False, False, False, False]: return "="
        elif data == [True, False, False, False]: return "A"
        elif data == [False, True, False, False]: return "B"
        elif data == [False, False, True, False]: return "C"
        elif data == [False, False, False, True]: return "D"
        elif data == [True, True, False, False]: return "F"
        elif data == [True, False, True, False]: return "G"
        elif data == [True, False, False, True]: return "H"
        elif data == [False, True, True, False]: return "J"
        elif data == [False, True, False, True]: return "K"
        elif data == [False, False, True, True]: return "M"
        elif data == [True, True, True, False]: return "P"
        elif data == [True, True, False, True]: return "Q"
        elif data == [True, False, True, True]: return "S"
        elif data == [False, True, True, True]: return "V"
        elif data == [True, True, True, True]: return "Z"
        else: return "Error"
    else:
        return data

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
            if CONFIG["img"]["interface"]:
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
# 載入座號定位圖片
number_template = read_image_file(safe_filename(f'{CONFIG["img"]["contrast_folder"]}/{CONFIG["img"]["number_template_file"]}'))


# 主程式
def main_function():
    global CONFIG
    
    # 確保有此資料夾
    folder_path = safe_filename(CONFIG["img"]["folder_path"])
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    error_message(f"查無此資料夾 以自動建立資料夾 {CONFIG['img']['folder_path']}", "warning")
    # 確保有答案
    have_ans = []
    # 記錄每題答錯人數
    question_error_count = [0]*CONFIG["score_setting"]["number_of_questions"]
    # 紀錄每人資料
    everyone_data = {}
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
                filename = "/".join(ans_file_split[:-1])
                check_is_ans_file = True
            elif ans_file_split[-1] == "nofile?.ansfile?":
                error_message(f"找不到指定的答案檔案", "wraning")
                continue
        elif not check_file_name in safe_text(CONFIG["img"]["format"]):
            error_message(f"{filename} 不是符合要求的圖片格式 以下是可接受的格式:\n{', '.join(CONFIG['img']['format'])}", "wraning")
            continue

        # 讀取影像
        if check_is_ans_file and CONFIG["img"]["interface"]:
            image = read_image_file(f"{filename}")
        else:
            image = read_image_file(f"{safe_filename(CONFIG['img']['folder_path'])}/{filename}")
        if image is None:
            error_message(f"讀取 {filename} 失敗", "wraning")
            continue

        # 影像預處理
        thresh = preprocess_image(image)
        # 檢測用放大圖片
        thresh = cv2.dilate(preprocess_image(image), None, iterations=2)
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
            error_message(f"{filename} 找不到有效的矩形", "wraning")
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
        use_image = cv2.resize(use_image, (CONFIG["find_table"]["crop_ratio_mult"]*12, CONFIG["find_table"]["crop_ratio_mult"]*13)) # 大概是12:13(寬:高)的比例
        
        # 儲存空白用
        # cv2.imwrite("minus_blank.png", use_image)

        # 尋找出定位點
        # 預處理圖片
        use_image_preprocess = preprocess_image(use_image) # 裁切後的原始圖片
        number_template_preprocess = preprocess_image(number_template) # 座號定位模板
        template_preprocess = preprocess_image(template) # 答案定位模板

        # 將原有答案卷部分清除 只保留劃記痕跡
        # use_image_blank = cv2.subtract(use_image_preprocess, minus_blank_preprocess) 
        # 影像預處理(相對於常用的預處理不太一樣 )
        use_img_gray = use_image if len(use_image.shape) == 2 else cv2.cvtColor(use_image, cv2.COLOR_BGR2GRAY)
        use_img_blur = cv2.GaussianBlur(use_img_gray, (3,3), 0)
        use_img_thresh = cv2.threshold(use_img_blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
        # 檢測水平線
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (100,1))
        horizontal_mask = cv2.morphologyEx(use_img_thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=1)
        # 檢測垂直線
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1,100))
        vertical_mask = cv2.morphologyEx(use_img_thresh, cv2.MORPH_OPEN, vertical_kernel, iterations=1)
        # 合併水平線和垂直線
        table_mask = cv2.bitwise_or(horizontal_mask, vertical_mask)
        # 將答案卷中線條清除
        use_image_blank = cv2.cvtColor(use_image_preprocess, cv2.COLOR_GRAY2BGR)
        use_image_blank[np.where(table_mask==255)] = [0,0,0] 
        use_image_blank = use_image_preprocess

        # # 檢查方向是否顛倒
        # # 答案座標
        # position_points = match_template(use_image_blank, template_preprocess, CONFIG)
        # np.random.shuffle(position_points)
        # # 號碼座標
        # position_points_number = match_template(use_image_blank, number_template_preprocess, CONFIG)
        # np.random.shuffle(position_points_number)
        # # 檢查圖片
        # if (position_points[0][2] < position_points_number[0][2]) and (position_points[-1][2] < position_points_number[-1][2]):
        #     error_message(f"{filename} 答案卷方向錯誤, 以自動轉正", "info")
        #     use_image_blank = cv2.rotate(use_image_blank, cv2.ROTATE_180)
        # elif (position_points[0][2] < position_points_number[0][2]):
        #     error_message(f"{filename} 答案卷疑似有問題, 結果可能有誤, 以自動轉正", "warning")
        #     use_image_blank = cv2.rotate(use_image_blank, cv2.ROTATE_180)

        # 取得答案
        # 計算匹配值
        position_points = match_template(use_image_preprocess, template_preprocess, CONFIG)
        # 存放答案用陣列
        all_ans_out = []
        # 計算寬度間隔
        position_quantity = len(position_points)
        each_lattice_width = (CONFIG["find_table"]["crop_ratio_mult"]*11) / (1 if position_quantity < 1 else position_quantity) / (CONFIG["find_table"]["number_of_answers"]+1)
        # 檢查用
        # ct = 0
        # clone = use_image.copy()
        ###
        break_check = False
        for position in sorted(position_points):
            # 計算高度間隔
            each_lattice_height = ((CONFIG["find_table"]["crop_ratio_mult"]*13)-position[1]) / (CONFIG["find_table"]["number_of_rows"]+1)
            # 計算格子座標
            ans_number_selected = []
            for number in range(CONFIG["find_table"]["number_of_rows"]):
                # 檢測超出範圍退出
                if len(all_ans_out)*CONFIG["find_table"]["number_of_rows"]+len(ans_number_selected) >= CONFIG["score_setting"]["number_of_questions"]:
                    break_check = True
                    break
                # 計算高度
                pos_y = position[1]+each_lattice_width/20 + (number+1)*each_lattice_height + number/3*each_lattice_height*0.1
                ans_selected_option = []
                for option in range(CONFIG["find_table"]["number_of_answers"]):
                    # 計算寬度
                    pos_x = position[0]-each_lattice_width/3.1 + (option+1)*each_lattice_width + option*each_lattice_width*0.065
                    
                    # 取得答案
                    get_ans_img = use_image_blank[int(pos_y-each_lattice_height/3):int(pos_y+each_lattice_height/3), int(pos_x):int(pos_x+each_lattice_width/1.5-(each_lattice_width/20 if option >= CONFIG["find_table"]["number_of_answers"]-1 else 0))]
                    
                    # 檢查用
                    # cv2.rectangle(clone, (int(pos_x), int(pos_y-each_lattice_height/3)), (int(pos_x+each_lattice_width/1.5-(each_lattice_width/20 if option >= CONFIG["find_table"]["number_of_answers"]-1 else 0)), int(pos_y+each_lattice_height/3)), (0, 0, 255), 1)
                    # cv2.imwrite(f"out.png", clone)
                    ###

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
                # 達到設定值退出
                
            all_ans_out.append(ans_number_selected)
            # 檢測退出
            if break_check:
                break
            
            # 檢查用
            # ct += 1
            # cv2.imwrite(f"out.png", clone)
            ###
        
        # 讀取座號
        # 計算匹配值 
        position_points_number = sorted(match_template(use_image_preprocess, number_template_preprocess, CONFIG), key=lambda x: x[1])
        
        # 計算座號
        # 檢查用
        # clone = use_image.copy()
        ###
        seat_number = ["", ""]
        if len(position_points_number) == 3:
            interval_height = abs(position_points_number[1][1]-position_points_number[0][1])
            for posnum in range(1, 3):
                position = position_points_number[posnum]
                pos_y = position[1]
                for num in range(10):
                    pos_x = position[0] - position[0]/13*(num+1) - position[0]*0.0015*(num) - position[0]*0.003*num/3
                    
                    # 取得座號
                    get_number_img = use_image_blank[int(pos_y-0.22*CONFIG["find_table"]["crop_ratio_mult"]):int(pos_y+0.16*CONFIG["find_table"]["crop_ratio_mult"]), int(pos_x-0.16*CONFIG["find_table"]["crop_ratio_mult"]):int(pos_x+0.16*CONFIG["find_table"]["crop_ratio_mult"])]
                    
                    # 檢查用
                    # cv2.rectangle(clone, (int(pos_x-0.16*CONFIG["find_table"]["crop_ratio_mult"]), int(pos_y-0.22*CONFIG["find_table"]["crop_ratio_mult"])), (int(pos_x+0.16*CONFIG["find_table"]["crop_ratio_mult"]), int(pos_y+0.16*CONFIG["find_table"]["crop_ratio_mult"])), (0, 0, 255), 3)
                    # cv2.imwrite(f"out.png", clone)
                    # cv2.imwrite(f"out.png", get_number_img)
                    ###

                    # 將座號放大
                    number_img_dilated = cv2.dilate(get_number_img, None, iterations=CONFIG["find_table"]["option_detect_expansion_degree"])
                    # 計算像素點數量
                    total_pixels = number_img_dilated.size
                    # 計算白色像素點數量
                    white_pixels = np.sum(number_img_dilated > 200)
                    # 計算比率
                    white_pixel_ratio = white_pixels/total_pixels*100
                    if white_pixel_ratio > CONFIG["find_table"]["option_detect_domain_value"]:
                        seat_number[posnum-1] += str(9-num)
                        break
            # 格式化座號
            image_number = format_number("".join(seat_number))
        else:
            # 無座號直接使用檔案名稱
            image_number = format_number(filename)
        
        # 紀錄時間
        write_csv(f'{safe_filename(CONFIG["read_write_log"]["log_file_name"])}', f">>現在時間", datetime.strftime(datetime.now(), "%Y年%m月%d日%H點%M分%S秒"))
        
        # 如果是答案就存起來
        if check_is_ans_file: 
            have_ans = all_ans_out.copy()
            save_data = [CONFIG["img"]["ans_file_name"], all_ans_out, 100]
            # everyone_data[CONFIG["img"]["ans_file_name"]] = [0, all_ans_out, CONFIG["score_setting"]["number_of_questions"], 100]
            write_csv(f'{safe_filename(CONFIG["read_write_log"]["log_file_name"])}', filename, save_data)
            error_message(f"已找到答案檔案 {filename} 並用於評分")
            continue

        
        # 確認是否有答案
        if len(have_ans) <= 0:
            # 儲存答案
            finish_check, finish_number = check_dict(everyone_data, image_number)
            save_data = [finish_number, all_ans_out, -1]
            everyone_data[finish_number] = [int(image_number) if image_number.isdigit() else image_number, all_ans_out, -1, -1]
            write_csv(f'{safe_filename(CONFIG["read_write_log"]["log_file_name"])}', filename, save_data)
        # 有答案
        else:
            # have_ans all_ans_out
            # 計算分數
            score_count = 0
            one_question_score = CONFIG["score_setting"]["total_score"]/CONFIG["score_setting"]["number_of_questions"]
            for column in range(len(all_ans_out)):
                for row in range(CONFIG["find_table"]["number_of_rows"]):
                    if (column*CONFIG["find_table"]["number_of_rows"]+row) >= CONFIG["score_setting"]["number_of_questions"]:break
                    if have_ans[column][row] == all_ans_out[column][row]:
                        score_count += 1
                        all_ans_out[column][row] = "-"
                    else:
                        question_error_count[column*CONFIG["find_table"]["number_of_rows"]+row] += 1
            score = math.ceil(score_count * one_question_score)
            # 儲存答案
            finish_check, finish_number = check_dict(everyone_data, image_number)
            save_data = [finish_number, all_ans_out, score]
            everyone_data[finish_number] = [int(image_number) if image_number.isdigit() else image_number, all_ans_out, score_count, score]
            write_csv(f'{safe_filename(CONFIG["read_write_log"]["log_file_name"])}', filename, save_data)
        continue

    # 將結果匯出成表格
    # 設定說明文字
    explanation_text = [
        "符號說明,答案正確:-,答案錯誤:呈現學生答案,未作答:=",
        "複選時代碼對照,A:A,B:B,C:C",
        "D:D,F:AB,G:AC,H:AD",
        "J:BC,K:BD,M:CD,P:ABC",
        "Q:ABD,S:ACD,V:BCD,Z:ABCD"
    ]
    explanation_count = 2
    output_file_name = f'{safe_filename_export(CONFIG["img"]["folder_path"])}'
    with open(f'{output_file_name}', "w", encoding="utf-8-sig") as csvfile:
        # 寫入正確答案 如沒有填入空白
        if len(have_ans) <= 0:
            csvfile.write("\\     ,"+f'標準答案  ,{"  ,"*CONFIG["score_setting"]["number_of_questions"]}答對題數,得分  ')
        else:
            csvfile.write("\\     ,"+f'標準答案  ,')
            for column in have_ans:
                for row in column:
                    csvfile.write(f" {convert_alphabet(row)},")
            csvfile.write(f'答對題數,得分  ')
        # 第一行說明
        csvfile.write(f",{explanation_text[0]}\n")
        # 寫入題號
        csvfile.write("座號  ,題號      ,",)
        for num in range(CONFIG["score_setting"]["number_of_questions"]):
            csvfile.write(f"{str(num+1).zfill(2)},")
        # 第二行說明
        csvfile.write(f'{" "*8},{" "*6},{explanation_text[1]}\n')
        # 寫入學生答案
        total_score = []
        for number in sorted(everyone_data.items(), key=lambda x: (x[0])):
            csvfile.write(f'{number[0]:4s}號,學生答案  ,')
            for column in number[1][1]:
                for row in column:
                    csvfile.write(f" {convert_alphabet(row)},")
            csvfile.write(f'{str(number[1][2]):8s},{str(number[1][3]):6s}')
            # 寫入後續說明
            if explanation_count < len(explanation_text):
                csvfile.write(f',{explanation_text[explanation_count]}\n')
                explanation_count += 1
            else:
                csvfile.write('\n')
            total_score.append(number[1][3])
        # 補足說明部分
        while explanation_count < len(explanation_text):
            csvfile.write(f'{" "*6},{" "*10},{"  ,"*CONFIG["score_setting"]["number_of_questions"]}{" "*8},{" "*6},{explanation_text[explanation_count]}\n')
            explanation_count += 1
        csvfile.write(f'\\     ,答錯人數  ,')
        for count in question_error_count:
            csvfile.write(f'{str(count).zfill(2)},')
        # 寫入平均
        total_score = [score for score in total_score if score != -1]
        if len(have_ans) <= 0: total_score = [0]
        csvfile.write(f'平均    ,{sum(total_score)/len(total_score):<6.1f}\n')
        # 最高分
        csvfile.write(f'{" "*6},{" "*10},{"  ,"*CONFIG["score_setting"]["number_of_questions"]}最高分  ,{max(total_score):<6d}\n')
        # 最低分
        csvfile.write(f'{" "*6},{" "*10},{"  ,"*CONFIG["score_setting"]["number_of_questions"]}最低分  ,{min(total_score):<6d}\n')

    return output_file_name

# 頁面用函數
def run_script(pdf_file, number_of_questions, total_score, ans_file):
    global CONFIG
    # 檢查檔案
    if not pdf_file: raise gr.Error("請上傳檔案", title="錯誤")

    # 建立資料夾
    work_folder = os.path.join(CONFIG["img"]["pdf_to_img_folder"], datetime.now().strftime("%Y%m%d%H%M%S"))
    os.makedirs(work_folder, exist_ok=True)
    # 轉換資料夾
    # pdf_doc = Document(pdf_file)
    # for dct in range(len(pdf_doc)):
    #     for img in pdf_doc.get_page_images(dct):
    #         xref = img[0]
    #         pix = Pixmap(pdf_doc, xref)
    #         pix.save(os.path.join(work_folder, f'{dct}_{hashlib.md5(f"img_{dct+1}_datetime.now()".encode()).hexdigest()}.png'))
    pdf_doc = PdfReader(pdf_file.name)
    for page_num, pdf_page in enumerate(pdf_doc.pages):  # 使用 enumerate 為頁面編號
        for pdf_image in pdf_page.images:  # 使用圖片索引確保唯一性
            # 使用頁碼和圖片名稱來生成唯一檔名
            image_path = os.path.join(work_folder, f'{page_num}_{hashlib.md5(f"{pdf_image.name}_{page_num + 1}_{datetime.now()}".encode()).hexdigest()}')
            with open(f"{image_path}.png", "wb") as pdf_path:
                pdf_path.write(pdf_image.data)
    # 將資料寫入設定檔
    CONFIG["img"]["folder_path"] = work_folder
    CONFIG["score_setting"]["number_of_questions"] = number_of_questions
    CONFIG["score_setting"]["total_score"] = total_score
    CONFIG["img"]["ans_file_name"] = ans_file.name if ans_file else ""
    output_file_name = main_function()
    return output_file_name



# 執行程式
if __name__ == "__main__":
    if CONFIG["img"]["interface"]:
        # 建立介面
        iface = gr.Interface(
            fn=run_script,
            inputs=[
                gr.File(label="上傳檔案", file_types=[".pdf"]),
                gr.Slider(minimum=1, maximum=50, label="輸入題目數量", step=1, value=50),
                gr.Slider(minimum=1, maximum=100, label="輸入總分", value=100),
                gr.File(label="上傳上傳答案檔")
            ],
            outputs=[
                gr.File(label="下載檔案", type="filepath")
            ],
            title="智慧視覺閱卷系統",
            description="上傳掃描過後的答案卷來自動評分",
            submit_btn = "一鍵執行"
        )
        iface.launch(share=True, inbrowser=True) # 自動於瀏覽器中開啟
    else:
        main_function()



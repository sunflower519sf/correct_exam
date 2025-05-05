import gradio as gr
import os
from pypdf import PdfReader
from datetime import datetime
import yaml
import math

# 載入配置文件
with open("config.yaml", "r", encoding="utf-8") as fr:
    CONFIG = yaml.safe_load(fr)

# 後端主函式，增加了 is_input_answers 以及答案列表參數（最多50個，根據題數取前面部分）
def run_script(pdf_file, number_of_questions, total_score, is_input_answers, *answers):
    if not pdf_file:
        raise gr.Error("請上傳檔案", title="錯誤")

    # 檢查並取出答案（若使用者選擇輸入答案）
    if is_input_answers:
        # 僅取前 number_of_questions 個答案（其餘隱藏）
        input_answers = list(answers)[:number_of_questions]
    else:
        input_answers = None

    # 建立資料夾
    work_folder = os.path.join(CONFIG["img"]["pdf_to_img_folder"], datetime.now().strftime("%Y%m%d%H%M%S"))
    os.makedirs(work_folder, exist_ok=True)

    # 讀取 PDF 並將內含圖片存檔
    pdf_doc = PdfReader(pdf_file.name)
    for pdf_page in pdf_doc.pages:
        for pdf_image in pdf_page.images:
            image_path = os.path.join(work_folder, pdf_image.name)
            with open(image_path, "wb") as f:
                f.write(pdf_image.data)

    # 這裡僅回傳上傳檔案名稱與（若有）答案資訊供參考
    result = f"處理檔案: {pdf_file.name}\n題目數量: {number_of_questions}\n總分: {total_score}"
    if input_answers is not None:
        result += f"\n使用者答案: {input_answers}"
    else:
        result += "\n未選擇輸入答案"
    return result

# 使用 gr.Blocks 建立更彈性的介面
with gr.Blocks() as demo:
    gr.Markdown("# 視覺化讀卡工具")
    with gr.Row():
        pdf_file = gr.File(label="上傳檔案", file_types=[".pdf"])
        number_of_questions = gr.Slider(minimum=1, maximum=50, label="題目數量", step=1, value=10)
        total_score = gr.Slider(minimum=1, maximum=100, label="總分", step=5, value=100)
    is_input_answers = gr.Checkbox(label="是否輸入答案", value=False)
    
    # 建立一個容器，內含答案輸入的格子（預設隱藏）
    answers_container = gr.Column(visible=False)
    
    # 從 CONFIG 中取得每列格子數，若未設定則預設為10
    grid_columns = CONFIG.get("grid_columns", 10)
    max_questions = 50  # 預設上限
    # 先產生最多50個 Radio 元件，分成多列排列
    answer_radios = []
    with answers_container:
        # 動態計算所需列數（以上限50題為例）
        rows = math.ceil(max_questions / grid_columns)
        for r in range(rows):
            with gr.Row():
                for c in range(grid_columns):
                    idx = r * grid_columns + c
                    if idx < max_questions:
                        # 初始設為隱藏，待勾選後依題數更新顯示
                        radio = gr.Radio(choices=["A", "B", "C", "D"], label=f"題 {idx+1}", visible=False)
                        answer_radios.append(radio)
    
    # 更新答案區域的顯示：根據「是否輸入答案」及「題目數量」動態顯示所需 Radio 元件
    def update_answer_grid(is_input, num_q):
        updates = []
        for idx in range(max_questions):
            if is_input and idx < num_q:
                updates.append(gr.update(visible=True))
            else:
                updates.append(gr.update(visible=False))
        # 同時更新答案容器的可見性
        container_update = gr.update(visible=is_input)
        # 第一個輸出回傳容器更新，其餘依序為各 Radio 的更新
        return [container_update] + updates

    # 設定變動事件，注意 outputs 的順序需與回傳結果對應
    # 第一個為答案容器，後續依序為所有答案 Radio
    inputs_for_update = [is_input_answers, number_of_questions]
    outputs_for_update = [answers_container] + answer_radios
    is_input_answers.change(
        fn=update_answer_grid,
        inputs=inputs_for_update,
        outputs=outputs_for_update
    )
    number_of_questions.change(
        fn=update_answer_grid,
        inputs=inputs_for_update,
        outputs=outputs_for_update
    )
    
    submit_btn = gr.Button("一鍵執行")
    output_text = gr.Textbox(label="結果")
    # 點選執行時，傳入所有元件的值（注意答案部分會傳回50個值，函式內取前 num_q 個）
    submit_btn.click(
        fn=run_script,
        inputs=[pdf_file, number_of_questions, total_score, is_input_answers] + answer_radios,
        outputs=output_text
    )

if __name__ == "__main__":
    demo.launch(inbrowser=True)

print("done")
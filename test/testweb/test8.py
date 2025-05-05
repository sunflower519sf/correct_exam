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
def run_script(pdf_file, number_of_questions, total_score, is_input_answers, answer_file, *answers):
    if not pdf_file:
        raise gr.Error("請上傳檔案", title="錯誤")

    # 檢查並取出答案（若使用者選擇輸入答案）
    if is_input_answers:
        input_answers = list(answers)[:number_of_questions]
    else:
        input_answers = answer_file.name if answer_file else "未上傳答案檔案"

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
    result += f"\n答案來源: {input_answers}"
    return result

# 使用 gr.Blocks 建立更彈性的介面
with gr.Blocks() as demo:
    gr.Markdown("# 視覺化讀卡工具")
    with gr.Row():
        with gr.Column():
            pdf_file = gr.File(label="上傳檔案", file_types=[".pdf"])
            with gr.Row():
                total_score = gr.Number(label="總分", value=100)
                number_of_questions = gr.Number(label="題目數量", value=10)
        with gr.Column():
            is_input_answers = gr.Checkbox(label="是否輸入答案", value=False)
            answer_file = gr.File(label="上傳答案檔案", file_types=[".txt"], visible=True)
            answers_container = gr.Column(visible=False)
            
            grid_columns = CONFIG.get("grid_columns", 10)
            max_questions = 50  # 預設上限
            answer_radios = []
            with answers_container:
                rows = math.ceil(max_questions / grid_columns)
                for r in range(rows):
                    with gr.Row():
                        for c in range(grid_columns):
                            idx = r * grid_columns + c
                            if idx < max_questions:
                                radio = gr.Radio(choices=["A", "B", "C", "D"], label=f"題 {idx+1}", visible=False)
                                answer_radios.append(radio)

    def update_answer_input(is_input):
        return gr.update(visible=is_input), gr.update(visible=not is_input)

    def update_answer_grid(is_input, num_q):
        updates = []
        for idx in range(max_questions):
            if is_input and idx < num_q:
                updates.append(gr.update(visible=True))
            else:
                updates.append(gr.update(visible=False))
        container_update = gr.update(visible=is_input)
        return [container_update] + updates
    
    inputs_for_update = [is_input_answers, number_of_questions]
    outputs_for_update = [answers_container] + answer_radios
    is_input_answers.change(fn=update_answer_grid, inputs=inputs_for_update, outputs=outputs_for_update)
    is_input_answers.change(fn=update_answer_input, inputs=[is_input_answers], outputs=[answers_container, answer_file])
    number_of_questions.change(fn=update_answer_grid, inputs=inputs_for_update, outputs=outputs_for_update)

    submit_btn = gr.Button("一鍵執行")
    output_text = gr.Textbox(label="結果")
    submit_btn.click(
        fn=run_script,
        inputs=[pdf_file, number_of_questions, total_score, is_input_answers, answer_file] + answer_radios,
        outputs=output_text
    )

if __name__ == "__main__":
    demo.launch(inbrowser=True)

print("done")

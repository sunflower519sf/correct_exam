import gradio as gr 
import os
from pypdf import PdfReader
from datetime import datetime
import yaml
import time

# 載入配置文件
with open("config.yaml", "r", encoding="utf-8") as fr:
    CONFIG = yaml.safe_load(fr)


def run_script(pdf_file, number_of_questions, total_score):
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
    #         pix.save(os.path.join(work_folder, f'img_{dct}.png'))
    pdf_doc = PdfReader(pdf_file.name)
    for pdf_page in pdf_doc.pages:
        for pdf_image in pdf_page.images:
            with open(os.path.join(work_folder, pdf_image.name), "wb") as pdf_path:
                pdf_path.write(pdf_image.data)

    
    

    
    return f"{pdf_file.name}"

# 建立介面
with gr.Blocks(title="視覺化讀卡工具") as demo:
    gr.Markdown("# 視覺化讀卡工具")
    # 上傳pdf和設定資料
    with gr.Row():
        pdf_file = gr.File(label="上傳檔案", file_types=[".pdf"])
        with gr.Column():
            total_score = gr.Number(label="總分", value=100, interactive=True)
            number_of_questions = gr.Number(label="題目數量", value=10, interactive=True)
    # 輸入題目
    with gr.Row():
        is_input_answers = gr.Checkbox(label="是否輸入答案", value=True)
        answer_file = gr.File(label="上傳答案檔案", file_types=[".txt"], visible=False)
        answers_container = gr.Column(visible=True)
        
        max_questions = 50  
        CONFIG["find_table"]["max_number"] # 題目上限
        for x_row in range():pass
        with answers_container:pass

    
    submit_btn = gr.Button("一鍵執行")
    output_text = gr.Textbox(label="結果")
    submit_btn.click(
        fn=run_script,
        inputs=[pdf_file, number_of_questions, total_score, is_input_answers, answer_file] + answer_radios,
        outputs=output_text
    )

if __name__ == "__main__":
    demo.launch(inbrowser=True) # 自動於瀏覽器中開啟

print("完成")
import gradio as gr # launch(share=True)
import os
from fitz import Document, Pixmap
from datetime import datetime
import yaml

# 載入配置文件
with open("config.yaml", "r", encoding="utf-8") as fr:
    CONFIG = yaml.safe_load(fr)


def run_script(pdf_file, number_of_questions, total_score):
    # 檢查檔案
    if not pdf_file: raise gr.in("請上傳檔案", title="錯誤")

    # 建立資料夾
    work_folder = os.path.join(CONFIG["img"]["pdf_to_img_folder"], datetime.now().strftime("%Y%m%d%H%M%S"))
    os.makedirs(work_folder, exist_ok=True)
    # 轉換資料夾
    pdf_doc = Document(pdf_file)
    for dct in range(len(pdf_doc)):
        for img in pdf_doc.get_page_images(dct):
            xref = img[0]
            pix = Pixmap(pdf_doc, xref)
            pix.save(os.path.join(work_folder, f'img_{dct}.png'))

    
    return f"{pdf_file.name}"

# Create a Gradio interface
iface = gr.Interface(
    fn=run_script,
    inputs=[
        gr.File(label="上傳檔案", file_types=["pdf"]),
        gr.Slider(minimum=1, maximum=50, label="題目數量", step=1),
        gr.Slider(minimum=1, maximum=100, label="總分", step=5)
    ],
    outputs=[
        "text"
    ],
    title="視覺化讀卡工具",
    description="上傳掃描過後的答案卡來自動評分",
    submit_btn = "一鍵執行"
)

if __name__ == "__main__":

    # iface.launch(share=True)
    iface.launch(inbrowser=True) # 自動於瀏覽器中開啟

print("done")
import gradio as gr

def process_file(file):
    if file is not None:
        # 獲取文件路徑
        file_path = file.name  # Gradio 提供文件的名稱
        return f"上傳的文件路徑：{file_path}"
    return "未上傳任何文件"

info_text = """
### 請上傳以下格式的文件：
- PNG
- JPG
- JPEG

請拖放文件到下面的區域或點擊上傳按鈕。
"""

# 創建 Gradio 界面
interface = gr.Interface(
    fn=process_file,  # 文件上傳時要執行的函數
    inputs=gr.File(label="上傳文件", type="filepath"),  # 文件上傳的輸入組件
    outputs="text",  # 顯示文件路徑的輸出組件
    live=True,  # 啟動即時預覽功能
    title="文件上傳測試",  # 視窗標題
    description=info_text  # 視窗描述
)

# 啟動界面
interface.launch()

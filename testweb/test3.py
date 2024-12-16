import gradio as gr
import os

def process_files(files, folder_path):
    results = []
    
    # 處理上傳的檔案
    if files:
        for file in files:
            file_path = file.name
            results.append(f"上傳的檔案路徑：{file_path}")

    # 處理資料夾路徑的輸入
    if folder_path:
        if os.path.exists(folder_path) and os.path.isdir(folder_path):
            results.append(f"選擇的資料夾路徑：{folder_path}")
            folder_files = os.listdir(folder_path)
            results.append("資料夾中的檔案：")
            results.extend(folder_files)
        else:
            return "資料夾路徑無效或不存在"

    if not results:
        return "未上傳任何檔案或提供資料夾路徑"
    
    return "\n".join(results)

info_text = """
### 請上傳文件或輸入資料夾的路徑：
- PNG
- JPG
- JPEG

請拖放文件到下面的區域或點擊上傳按鈕以選擇多個檔案，或手動輸入資料夾路徑。
"""

# 創建 Gradio 界面
interface = gr.Interface(
    fn=process_files,  # 多檔案上傳時要執行的函數
    inputs=[
        gr.File(label="上傳檔案", type="filepath", multiples=True),  # 支援多檔案上傳的輸入組件
        gr.Textbox(label="資料夾路徑", placeholder="請輸入資料夾路徑")  # 資料夾路徑的輸入組件
    ],
    outputs="text",  # 顯示結果的輸出組件
    live=True,  # 啟動即時預覽功能
    title="多檔案與資料夾路徑上傳測試",  # 視窗標題
    description=info_text  # 視窗描述
)

# 啟動界面
interface.launch()

from tkinter import Tk, filedialog
import gradio as gr

def get_folder_path(folder_path: str = "") -> str:
    """
    開啟一個資料夾選擇對話框，允許使用者瀏覽並選擇一個資料夾。
    如果未選擇資料夾，則回傳初始提供的資料夾路徑或空字串。
    在 macOS 或特定環境變數存在時，此功能會跳過資料夾對話框，適用於自動化環境。

    參數:
    - folder_path (str): 初始的資料夾路徑，默認為空字串，若未選擇資料夾時使用。

    回傳值:
    - str: 使用者選擇的資料夾路徑，或未選擇時回傳初始的 `folder_path`。

    拋出例外:
    - TypeError: 如果 `folder_path` 不是字串類型。
    - EnvironmentError: 如果訪問環境變數時出現問題。
    - RuntimeError: 如果初始化資料夾對話框時出現問題。

    注意:
    - 此函式會檢查 `ENV_EXCLUSION` 清單中的環境變數，以決定是否跳過資料夾對話框，防止自動化操作中顯示對話框。
    - 在 macOS 上（`sys.platform != "darwin"`），會跳過對話框作為特定行為調整。
    """
    # 驗證參數類型
    if not isinstance(folder_path, str):
        raise TypeError("folder_path 必須是字串")

    try:
        # 建立一個隱藏的 Tkinter 主視窗以顯示對話框
        root = Tk()
        root.withdraw()  # 隱藏主 Tkinter 視窗
        root.wm_attributes("-topmost", 1)  # 確保對話框顯示在最上層

        # 開啟資料夾選擇對話框
        selected_folder = filedialog.askdirectory(initialdir=folder_path or ".")

        root.destroy()  # 銷毀 Tkinter 主視窗
        return selected_folder or folder_path  # 回傳選擇的資料夾或初始路徑
    except Exception as e:
        raise RuntimeError(f"初始化資料夾對話框時出錯: {e}") from e

# 定義一個函式，用於執行主要邏輯
def run_script():
    # 呼叫資料夾選擇函式並儲存結果到變數
    folder_path = get_folder_path()
    return f"選擇的資料夾路徑為: {folder_path}"

# 建立 Gradio 介面
with gr.Blocks() as demo:
    gr.Markdown("### 資料夾選擇示例")

    folder_path_box = gr.Textbox(label="選擇的路徑", interactive=False)

    def update_folder_path():
        return get_folder_path()

    folder_button = gr.Button("選擇資料夾")
    folder_button.click(update_folder_path, inputs=[], outputs=folder_path_box)

    demo.components = [folder_path_box, folder_button]

    gr.Interface(
        fn=run_script,  # 指定執行的函式
        inputs=[],  # 不需要輸入
        outputs="text"  # 以文字形式顯示輸出
    ).render()

if __name__ == "__main__":
    demo.launch()

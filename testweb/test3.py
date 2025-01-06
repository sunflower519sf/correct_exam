import gradio as gr

def process_files(files):
    file_paths = [file.name for file in files]
    return f"上傳的檔案路徑：{file_paths}"

iface = gr.Interface(
    fn=process_files,
    inputs=gr.Files(label="請上傳檔案"),
    outputs="text"
)

iface.launch()

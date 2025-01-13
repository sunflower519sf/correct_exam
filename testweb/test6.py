import gradio as gr

def process_files(files):
    # Retrieve the names of the uploaded files
    file_paths = [file.name for file in files]
    return f"Uploaded file paths: {file_paths}"

interface = gr.Interface(
    fn=process_files,
    inputs=gr.Files(label="上傳檔案"),
    outputs="text"
)

# Launch the interface
interface.launch()

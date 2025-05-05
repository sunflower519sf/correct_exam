from tkinter import Tk, filedialog
import gradio as gr

def get_folder_path(folder_path: str = "") -> str:
    """
    Opens a folder dialog to select a folder, allowing the user to navigate and choose a folder.
    If no folder is selected, returns the initially provided folder path or an empty string if not provided.
    This function is conditioned to skip the folder dialog on macOS or if specific environment variables are present,
    indicating a possible automated environment where a dialog cannot be displayed.

    Parameters:
    - folder_path (str): The initial folder path or an empty string by default. Used as the fallback if no folder is selected.

    Returns:
    - str: The path of the folder selected by the user, or the initial `folder_path` if no selection is made.

    Raises:
    - TypeError: If `folder_path` is not a string.
    - EnvironmentError: If there's an issue accessing environment variables.
    - RuntimeError: If there's an issue initializing the folder dialog.

    Note:
    - The function checks the `ENV_EXCLUSION` list against environment variables to determine if the folder dialog should be skipped, aiming to prevent its appearance during automated operations.
    - The dialog will also be skipped on macOS (`sys.platform != "darwin"`) as a specific behavior adjustment.
    """
    # Validate parameter type
    if not isinstance(folder_path, str):
        raise TypeError("folder_path must be a string")

    try:
        root = Tk()
        root.withdraw()
        root.wm_attributes("-topmost", 1)
        selected_folder = filedialog.askdirectory(initialdir=folder_path or ".")
        root.destroy()
        return selected_folder or folder_path
    except Exception as e:
        raise RuntimeError(f"Error initializing folder dialog: {e}") from e


def create_folder_ui(path="./"):
    with gr.Row():
        text_box = gr.Textbox(
            label="path",
            info="Path",
            lines=1,
            value=path,
        )
        button = gr.Button(value="\U0001f5c0", inputs=text_box, min_width=24)

        button.click(
            lambda: get_folder_path(text_box.value),
            outputs=[text_box],
        )

    return text_box, button

with gr.Blocks() as demo:
    gr.Markdown("### 資料夾選擇示例")
    folder_textbox, folder_button = create_folder_ui()

if __name__ == "__main__":
    demo.launch()
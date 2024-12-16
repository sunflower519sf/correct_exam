import gradio as gr # launch(share=True)
import subprocess

def run_script(test, checkbox):
    # Execute the main.py script
    
    return "main.py has been executed."

# Create a Gradio interface
iface = gr.Interface(
    fn=run_script, 
    inputs=["text"], 
    outputs="text",
    clear_btn=None
)

if __name__ == "__main__":

    # iface.launch(share=True)
    iface.launch()
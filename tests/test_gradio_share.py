import gradio as gr

def greet(name):
    return "Hello " + name + "!"

demo = gr.Interface(fn=greet, inputs="text", outputs="text")

if __name__ == "__main__":
    print("Testing Gradio sharing on port 7865...")
    try:
        demo.launch(share=True, server_port=7865)
    except Exception as e:
        print(f"Minimal share test failed: {e}")

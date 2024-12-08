import os
import shutil
import gradio as gr
import modelscope_studio as mgr
import warnings
warnings.filterwarnings("ignore")

os.environ["is_half"] = "True"



shutil.rmtree('./workspaces/results', ignore_errors= True)

from src.pipeline import chat_pipeline

with gr.Blocks() as demo:   
    gr.Markdown(
        """
        <div style="text-align: center; font-size: 32px; font-weight: bold; margin-bottom: 20px;">
        Elder Fin-Assistant
        </div>  
        """
    )
    with gr.Row():
        with gr.Column(scale = 2):
            user_chatbot = mgr.Chatbot(
                label = "Chat History 💬",
                value = [[None, {"text":"您好，请问有什么可以帮到您？您可以在下方的输入框点击麦克风录制音频或直接输入文本与我聊天。"}],],
                avatar_images=[
                    {"avatar": os.path.abspath("data/icon/user.png")},
                    {"avatar": os.path.abspath("data/icon/assistant.png")},
                ],
                height= 750,
                ) 

            user_input = mgr.MultimodalInput(sources=["microphone"])

        with gr.Column(scale = 1):
            video_stream = gr.Video(label="Video Stream 🎬 (基于Gradio 5测试版，网速不佳可能卡顿)", streaming=True, height = 500, scale = 1)  
            stop_button = gr.Button(value="停止生成")

    user_messages = gr.State([{'role': 'system', 'content': None}])
    user_processing_flag = gr.State(False)
    lifecycle = mgr.Lifecycle()


    lifecycle.mount(chat_pipeline.load_voice,
        inputs=[],
        outputs=[user_input]
    )

    user_input.submit(chat_pipeline.run_pipeline,
        inputs=[user_input, user_messages], 
        outputs=[user_messages]
        )
    user_input.submit(chat_pipeline.yield_results, 
        inputs=[user_input, user_chatbot, user_processing_flag],
        outputs = [user_input, user_chatbot, video_stream, user_processing_flag]
        )

    lifecycle.unmount(chat_pipeline.stop_pipeline, 
        inputs = user_processing_flag, 
        outputs = user_processing_flag
        )

    stop_button.click(chat_pipeline.stop_pipeline, 
        inputs = user_processing_flag, 
        outputs = user_processing_flag
        )

demo.launch()
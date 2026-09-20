import gradio as gr


def reverse_text(text):
    return text[::-2]



def hellotoPerson(name):
    return "你好"+name

# 界面配置
demo = gr.Interface(
    fn=hellotoPerson,#调用reserse_text函数
    inputs="text",# 输入组件类型为文本
    outputs="text",# 输出类型为文本
)


# 启动应用
demo.launch()
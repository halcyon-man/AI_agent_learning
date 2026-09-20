# 指令模板
from ai_agent_1 import TAVILY_API_KEY

AGENT_SYSTEM_PROMPT = """
你是一个智能旅行助手。你的任务是分析用户的请求，并使用可用工具一步步地解决问题。

# 可用工具:
- `get_weather(city: str)`: 查询指定城市的实时天气。
- `get_attraction(city: str, weather: str)`: 根据城市和天气搜索推荐的旅游景点。

# 输出格式要求:
你的每次回复必须严格遵循以下格式，包含一对Thought和Action：

Thought: [你的思考过程和下一步计划]
Action: [你要执行的具体行动]

Action的格式必须是以下之一：
1. 调用工具：function_name(arg_name="arg_value")
2. 结束任务：Finish[最终答案]

# 重要提示:
- 每次只输出一对Thought-Action
- Action必须在同一行，不要换行
- 当收集到足够信息可以回答用户问题时，必须使用 Action: Finish[最终答案] 格式结束

请开始吧！
"""
import requests
# 1.获取天去的工具
def get_weather(city:str):
    url=f"https://wttr.in/{city}?format=j1"
    try:
        # 获取信息
        response=requests.get(url)

        # 检查状态
        response.raise_for_status()

        #获取当前天气状况

        current_condition=response["current_condition"][0]

        # 获取天气
        weather_des=current_condition["weatherDes"][0]["value"]

        # 获取当前温度
        temp_c=current_condition["temp_c"]


        return f"这个{city}的天气是{weather_des},气温为{temp_c}摄氏度。"

    except requests.exceptions.RequestException as e:
        return f"错误，查询天气时遇到网络问题-{e}"
    except (KeyError,IndexError) as e:
        return f"错误:天气数据解析失败，可能是城市名无效-{e}"



import os
from tavily import TavilyClient
# 2.获取景点工具
def get_attraction(city:str,weather:str)->str:
    api_key=os.environ.get("TAVILY_API_KEY")
    if  not api_key:
        print(f"错误，未找到TAVILY_API_KEY,请重新配置")

    try:
        query=f"{city}的气温为{weather}摄氏度的时候，有哪些景点适合游玩并给出简单的理由"
        client=TavilyClient(api_key=api_key)
        # 调用API进行联网搜索，并总结回答
        res=client.search(query=query,search_depth="basic",include_answer=True)
        # 有总结性的回答直接返回
        if res["answer"]:
            return res["answer"]
        # 没有总结性的直接格式化
        formatted_results=[]
        for result in res["result"]:
            title = result["title"]
            content = result["content"]
            text = f"【{title}】\n{content}"
            formatted_results.append(text)
        if not formatted_results:
            return f"抱歉，怎么找到合适的景点"
        # join是能拼接字符串
        return "根据搜索，为您找到以下信息:\n" + "\n".join(formatted_results)
    except Exception as e:
        return f"错误:执行Tavily搜索时出现问题 - {e}"
# 3.定义工具箱
available_tools={
    "get_weather":get_weather,
    "get_attraction":get_attraction
}

# 4.接入大模型
from openai import OpenAI

class OpenAICompatibleClient:
    """
    一个用于调用任何兼容OpenAI接口的LLM服务端。
    """
    def __init__(self,model:str,api_key:str,base_url:str):
        self.model=model
        self.client=OpenAI(api_key=api_key,base_url=base_url)


    def generate(self,prompt:str,system_prompt:str)->str:
        """调用LLM API 来生成回应"""
        print("正在调用大语言模型...")
        try:
            messages = [
                {"role":'system','content':system_prompt},
                {"role":'user','content':prompt}
            ]
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=False
            )
            answer =  response.choices[0].message.content
            print("大语言模型响应成功")
            return answer
        except Exception as e:
            print(f"调用LLM API时发生错误：{e}")
            return "错误：调用语言模型服务时出错"


import re

# --- 1. 配置LLM客户端 ---
# 请根据您使用的服务，将这里替换成对应的凭证和地址
API_KEY = "YOUR_API_KEY"
BASE_URL = "YOUR_BASE_URL"
MODEL_ID = "YOUR_MODEL_ID"
TAVILY_API_KEY = "YOUR_Tavily_KEY"
os.environ['TAVILY_API_KEY'] = "YOUR_TAVILY_API_KEY"

llm = OpenAICompatibleClient(
    model=MODEL_ID,
    api_key=API_KEY,
    base_url=BASE_URL
)

# --- 2. 初始化 ---
user_prompt = "你好，请帮我查询一下今天北京的天气，然后根据天气推荐一个合适的旅游景点。"
prompt_history = [f"用户请求: {user_prompt}"]

print(f"用户输入: {user_prompt}\n" + "=" * 40)

# --- 3. 运行主循环 ---
for i in range(5):  # 设置最大循环次数
    print(f"--- 循环 {i + 1} ---\n")

    # 3.1. 构建Prompt
    full_prompt = "\n".join(prompt_history)

    # 3.2. 调用LLM进行思考
    llm_output = llm.generate(full_prompt, system_prompt=AGENT_SYSTEM_PROMPT)
    # 模型可能会输出多余的Thought-Action，需要截断
    match = re.search(r'(Thought:.*?Action:.*?)(?=\n\s*(?:Thought:|Action:|Observation:)|\Z)', llm_output, re.DOTALL)
    if match:
        truncated = match.group(1).strip()
        if truncated != llm_output.strip():
            llm_output = truncated
            print("已截断多余的 Thought-Action 对")
    print(f"模型输出:\n{llm_output}\n")
    prompt_history.append(llm_output)

    # 3.3. 解析并执行行动
    action_match = re.search(r"Action: (.*)", llm_output, re.DOTALL)
    if not action_match:
        observation = "错误: 未能解析到 Action 字段。请确保你的回复严格遵循 'Thought: ... Action: ...' 的格式。"
        observation_str = f"Observation: {observation}"
        print(f"{observation_str}\n" + "=" * 40)
        prompt_history.append(observation_str)
        continue
    action_str = action_match.group(1).strip()

    if action_str.startswith("Finish"):
        final_answer = re.match(r"Finish\[(.*)\]", action_str).group(1)
        print(f"任务完成，最终答案: {final_answer}")
        break

    tool_name = re.search(r"(\w+)\(", action_str).group(1)
    args_str = re.search(r"\((.*)\)", action_str).group(1)
    kwargs = dict(re.findall(r'(\w+)="([^"]*)"', args_str))

    if tool_name in available_tools:
        observation = available_tools[tool_name](**kwargs)
    else:
        observation = f"错误:未定义的工具 '{tool_name}'"

    # 3.4. 记录观察结果
    observation_str = f"Observation: {observation}"
    print(f"{observation_str}\n" + "=" * 40)
    prompt_history.append(observation_str)




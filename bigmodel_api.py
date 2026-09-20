# 调用智谱API
from http.client import responses

from zai import ZhipuAiClient
import os
from dotenv import load_dotenv
import json
# 从环境变量读取API Key
load_dotenv()
client = ZhipuAiClient(api_key=os.getenv("ZHIPUAI_API_KEY"))

# # 创建对话，使用glm-4.7-Flash模型，永久免费的
# messages=[{"role":"system","content":"你叫小智，只回答emoji"}]
# while True:
#     user_input=input("你：")
#     if user_input.lower()=="q":
#         break
#     # 把用户对话追进档案袋
#     messages.append({"role":"user","content":user_input})
#     responses=client.chat.completions.create(
#         model="glm-4-Flash",
#         messages=messages
#
#     )
#     assistant_reply= responses.choices[0].message.content
#     messages.append({"role":"assistant","content":assistant_reply})
#     print("AI:",assistant_reply)
#     print(f"当前记忆条数：{len(messages)}")


# 定义天气查询函数
def get_weather(city: str) -> dict:
    """获取指定城市的天气信息"""
    # 这里应该调用真实的天气 API
    weather_data = {
        "city": city,
        "temperature": "22°C",
        "condition": "晴天",
        "humidity": "65%",
        "wind_speed": "5 km/h"
    }
    return weather_data


# 定义函数工具
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "获取指定城市的当前天气信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名称，例如：北京、上海"
                    }
                },
                "required": ["city"]
            }
        }
    }
]

# 发起对话请求
response = client.chat.completions.create(
    model="glm-4-Flash",  # 使用支持函数调用的模型
    messages=[
        {"role": "user", "content": "北京今天天气怎么样？"}
    ],
    tools=tools,  # 传入函数工具
    tool_choice="auto"  # 自动选择是否调用函数
)

# 处理函数调用
message = response.choices[0].message
messages = [{"role": "user", "content": "北京今天天气怎么样？"}]
messages.append(message.model_dump())

if message.tool_calls:
    for tool_call in message.tool_calls:
        if tool_call.function.name == "get_weather":
            # 解析参数并调用函数
            args = json.loads(tool_call.function.arguments)
            weather_result = get_weather(args.get("city"))

            # 将函数结果返回给模型
            messages.append({
                "role": "tool",
                "content": json.dumps(weather_result, ensure_ascii=False),
                "tool_call_id": tool_call.id
            })

    # 获取最终回答
    final_response = client.chat.completions.create(
        model="glm-4-Flash",
        messages=messages,
        tools=tools
    )

    print(final_response.choices[0].message.content)
else:
    print(message.content)



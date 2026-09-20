from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import ModelFamily
from dotenv import load_dotenv
from autogen_core.models import UserMessage
import os
import asyncio
load_dotenv()

custom_model_client = OpenAIChatCompletionClient(
    model="glm-4-flash" or os.getenv("MODEL_ID"),
    base_url=os.getenv("base_url"),
    api_key=os.getenv("ZHIPUAI_API_KEY"),
    model_info={
        "vision":False,
        "function_calling":False,
        "structured_output":False,
        "family":'glm',
        'json_output':False,
    },)

# async def main() -> None:
#
#     messages=[UserMessage(content='你来自那里?',source='user')]
#
#     stream = custom_model_client.create_stream(messages=messages)
#     print('Streamed response:')
#     async for response in stream:
#         if isinstance(response,str):
#             print(response,flush=True,end="")
#         else:
#             print("\n\n---------------\n")
#             print("The complete response:",flush=True)
#             print(response.content,flush=True)
#
#     await custom_model_client.close()


# asyncio.run(main())


# 创建团队
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.base import TaskResult
from autogen_agentchat.conditions import ExternalTermination,TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_core import CancellationToken
from autogen_ext.models.openai import OpenAIChatCompletionClient

async def main():
        primary_agent = AssistantAgent(
            "primary",
            model_client=custom_model_client,
            system_message='你是一个有用的AI助手',
        )



        critic_agent = AssistantAgent(
            "critic",
            model_client=custom_model_client,
            system_message='你是一个审查员，请提供建设性的意见。当你的反馈被处理/解决后，请回复同意',
        )
        text_termination = TextMentionTermination("同意")
        team = RoundRobinGroupChat([primary_agent,critic_agent],termination_condition=text_termination)


        #1.整体输出
        # result = await team.run(task='你知道王阳明吗，他的生平是怎么样子的？')
        # print(result)

        await team.reset()

        # # 2.流式输出
        # async for message in team.run_stream(task='你知道王阳明吗，他的生平是怎么样的？'):
        #     if isinstance(message,TaskResult):
        #         print("Stop Reason:",message.stop_reason)
        #     else:
        #         print(message)
        #



        #3.结构化输出
        await Console(team.run_stream(task='你知道王阳明吗，他的生平是怎么样子的？'))
        await Console(team.run_stream(task="按照他的风格写一首唐代关于秋天的诗"))




asyncio.run(main())
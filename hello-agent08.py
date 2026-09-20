import os
import re
from openai import OpenAI
from dotenv import load_dotenv
from typing import List, Dict

# 加载 .env 文件中的环境变量
load_dotenv()


class HelloAgentsLLM:
    """
    为本书 "Hello Agents" 定制的LLM客户端。
    它用于调用任何兼容OpenAI接口的服务，并默认使用流式响应。
    """

    def __init__(self, model: str = None, apiKey: str = None, baseUrl: str = None, timeout: int = None):
        """
        初始化客户端。优先使用传入参数，如果未提供，则从环境变量加载。
        """
        self.model = model or os.getenv("MODEL_ID")
        apiKey = apiKey or os.getenv("ZHIPUAI_API_KEY")
        baseUrl = baseUrl or os.getenv("base_url")
        timeout = timeout or int(os.getenv("LLM_TIMEOUT", 60))

        if not all([self.model, apiKey, baseUrl]):
            raise ValueError("模型ID、API密钥和服务地址必须被提供或在.env文件中定义。")

        self.client = OpenAI(api_key=apiKey, base_url=baseUrl, timeout=timeout)

    def think(self, messages: List[Dict[str, str]], temperature: float = 0) -> str:
        """
        调用大语言模型进行思考，并返回其响应。
        """
        print(f"🧠 正在调用 {self.model} 模型...")
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                stream=True,
            )

            # 处理流式响应
            print("✅ 大语言模型响应成功:")
            collected_content = []
            for chunk in response:
                if not chunk.choices:
                    continue
                content = chunk.choices[0].delta.content or ""
                print(content, end="", flush=True)
                collected_content.append(content)
            print()  # 在流式输出结束后换行
            return "".join(collected_content)

        except Exception as e:
            print(f"❌ 调用LLM API时发生错误: {e}")
            return None


# --- 客户端使用示例 ---
# if __name__ == '__main__':
#     try:
#         llmClient = HelloAgentsLLM()
#
#         exampleMessages = [
#             {"role": "system", "content": "You are a helpful assistant that writes Python code."},
#             {"role": "user", "content": "写一个快速排序算法"}
#         ]
#
#         print("--- 调用LLM ---")
#         responseText = llmClient.think(exampleMessages)
#         if responseText:
#             print("\n\n--- 完整模型响应 ---")
#             print(responseText)
#
#     except ValueError as e:
#         print(e)




# 定义搜索方法
from serpapi import SerpApiClient

def search(query:str):
    api_key =os.getenv("SERPAPI_API_KEY")
    if not api_key:
        raise ValueError("请配置serpapi_api_key")
    params={
        "q":query,
        "api_key":api_key,
        "engine":"google",
        "h1":"zh-cn",
        "g1":"cn"
    }


    try:
        client = SerpApiClient(params)
        results = client.get_dict()

        # 智能解析:优先寻找最直接的答案
        if "answer_box_list" in results:
            return "\n".join(results["answer_box_list"])
        if "answer_box" in results and "answer" in results["answer_box"]:
            return results["answer_box"]["answer"]
        if "knowledge_graph" in results and "description" in results["knowledge_graph"]:
            return results["knowledge_graph"]["description"]
        if "organic_results" in results and results["organic_results"]:
            # 如果没有直接答案，则返回前三个有机结果的摘要
            snippets = [
                f"[{i + 1}] {res.get('title', '')}\n{res.get('snippet', '')}"
                for i, res in enumerate(results["organic_results"][:3])
            ]
            return "\n\n".join(snippets)

        return f"对不起，没有找到关于 '{query}' 的信息。"

    except Exception as e:
        return f"搜索时发生错误: {e}"


from typing import Dict,Any

class ToolExecutor():
    """
    用于管理和执行工具的工具执行器
    """
    def __init__(self):
        self.tools:Dict[str,Dict[str,Any]]={}

    def registerTool(self,name:str, description:str, func:callable):
        if name in self.tools:
            print(f'{name}已经存在，将覆盖')
        self.tools[name]={'description':description,'func':func}
        print(f'{name}工具成功注册')


    def getTool(self,name):
    #直接返回要执行的函数
        return self.tools[name].get('func')


    def getAvailableTools(self):

        return "\n".join(f'{name}:{info["description"]}' for name,info in self.tools.items())







# ReAct提示词模板
REACT_PROMPT_TAMPLATE="""
1.角色：
你是一名有用的助手，当你遇到需要工具来解决问题的时候你可以调用工具

2.可以使用的工具：
{tools}

3.格式与规划：
每一次都必须按照一下的格式输出：
Thought:写出你分析问题，拆解问题，规划解决方式
Action:你采取的行动必须是以下形式之一
-'{{tool_name}}[{{tool_input}}]':调用一个可用的工具
-'Finish[最终答案]':当你认为是最终答案时候
-当你觉得收集信息足够时，且能回答用户的时候，必须按照格式:Action：Finish[最终答案]输出

4.现在开始解决一下问题
Question:{question}
History:{history}
"""


# 定义ReActAgent类
class ReActAgent:
    def __init__(self,llm:HelloAgentsLLM, tools_executor:ToolExecutor):
        self.llm=llm
        self.tools_executor = tools_executor
        self.history= []



    def parse_output(self,text:str):
            thought_math = re.search(r"Thought:(.*?)(?=Action：|$)",text,re.DOTALL)
            action_math = re.search(r"Action:(.*?)",text,re.DOTALL)

            thought=thought_math.group(1).strip()

            action=action_math.group(1).strip()

            return thought,action


    def parse_action(self,action:str):
        match =re.search(r'(\w+)\[(.*)\]',action,re.DOTALL)
        if match:
            return match.group(1).strip(),match.group(2).strip()
        return None ,None


    def run(self,question:str,max_steps:int=5):

        # 1.初始化提示词
        self.history=[]
        current_step = 0

        while current_step < max_steps:
            current_step += 1
            tools_docs = self.tools_executor.getAvailableTools()
            history_str = "\n".join(self.history)
            prompt = REACT_PROMPT_TAMPLATE.format(
                question=question,
                history=history_str,
                tools=tools_docs
            )
            messages = [{'role':'user','content':prompt}]
            response = self.llm.think(messages=messages,temperature=0)
            if not response:
                print("查询不到答案")
                break
            thought,action = self.parse_output(response)
            if thought:
                print(f"thought:{thought}")
            if not action:
                print(f"警告:未能解析出有效的Action，流程终止。")
                break

            tool_name,tool_input=self.parse_action(action)
            if not tool_name or not tool_input:
                continue

            print(f"action:{tool_name}[{tool_input}]")
            tool_function = self.tools_executor.getTool(tool_name)
            if not tool_function:
                print(f"没用定义工具{tool_function}")
            else:
                observation=tool_function(tool_input)
                print(f"observation:{observation}")
                self.history.append(f"Action: {action}")
                self.history.append(f"Observation: {observation}")
        print("已达到最大步数，流程终止。")
        return None

if __name__=="__main__":
    llm=HelloAgentsLLM()
    tool_executor = ToolExecutor()
    description="你是一个搜索工具"
    tool_name = tool_executor.registerTool("Search",description=description,func=search)
    react_client=ReActAgent(llm=llm,tools_executor=tool_executor)
    question='请查询2026年9月13日，北京的天气'
    response=react_client.run(question=question)
    print(f"============最后结果==========")
    print(response)














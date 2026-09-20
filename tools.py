# 定义搜索方法
from serpapi import SerpApiClient
import os
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
        # 获取工具的信息

        return "\n".join(f'{name}:{info["description"]}' for name,info in self.tools.items())

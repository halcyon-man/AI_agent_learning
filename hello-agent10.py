import re
from llm_client import HelloAgentsLLM
from tools import ToolExecutor, search


# 1.提示词，统一格式
AGENT_SYSTEM_PROMPT="""
声明：你是一名可以调用外部工具解决问题的助手，当你遇到问题需要工具的时候你可以使用工具。

可使用工具：
{tools}

强制按照一下格式输出：
Thought:写你分析问题，拆解问题，规划问题，解决问题的过程
Action:{{tool_name}}:[{{tool_input}}]
    -tool_name:你调用工具的名称
    -tool_input:你调用工具后传入的参数
    -如果信息已经足够回答问题，Action只能写成固定格式：
    Action:Finish[最终回答文本]
    禁止换行、禁止额外文字、禁止再输出任何工具调用。
    只要你连续两次调用同一个Search工具且query完全一样，就必须立刻输出Finish，禁止重复搜索！
    
接下来请回答以下问题：

question:{question}
history:{history}

"""

# 创建ReAct Agent

class react_agent:

    def __init__(self,llm:HelloAgentsLLM, tool_executor:ToolExecutor):
        self.llm=llm
        self.tool_executor=tool_executor
        self.history=[]


    def run(self,question, max_step:int=3):
        self.history=[]
        count_step=0
        while count_step < max_step:
            count_step+=1
            # llm只认识字符串，所以拼接的是字符串
            history_str = "\n".join(self.history)
            print(f'----------第{count_step}步------：')
            tool_docs=self.tool_executor.getAvailableTools()
            prompt=AGENT_SYSTEM_PROMPT.format(
            tools=tool_docs,
            question=question,
            history=history_str
            )

            messages=[{'role':'user','content':prompt}]

            response=self.llm.think(messages=messages,temperature=0)
            thought,action = self.parse_output(response)
            if not thought or not action:
                # self.history.append(
                #     {"thought": "格式错误", "action": "", "observation": "LLM输出不符合Thought+Action格式"})
                self.history.append(f'thought:格式错误，action: ,observation:LLm输出不符合Thought+Action格式')
                print(f'输出格式错误跳出本轮循环')
                continue

            # print(f'思考：{thought}')
            # print(f'动作：{action}')

            final_answer=re.search(r'Finish(.*)',action,re.DOTALL)
            if final_answer:
                return final_answer.group(1).strip()
            tool_name,tool_input = self.parse_action(action)
            if not tool_name or not tool_input:
                continue
            observation={tool_name:tool_input}
            get_tool=self.tool_executor.getTool(tool_name)
            if not get_tool:
                print(f'工具{tool_name}不存在')
                continue
            res = get_tool(tool_input)
            self.history.append(f'action:{action},observation:{res}')
        print(f'已经执行到最后一步')
        return None



    # 正则获取thought、action
    def parse_output(self,response:str):
        thought_action_math=re.search(r'Thought:\s*(.*?)\nAction:\s*(.*)',response,re.DOTALL)
        if thought_action_math:
            thought = thought_action_math.group(1).strip()
            action = thought_action_math.group(2).strip()
            return thought, action
        return None,None

    # 正则获取action的工具名和输入
    def parse_action(self,action):
        if not action:
            return None,None
        tool_name_input= re.search(r'(.*?):\[(.*)\]',action,re.DOTALL)
        if tool_name_input:
            tool_name = tool_name_input.group(1)
            tool_input = tool_name_input.group(2)
            if tool_name and tool_input:
                return tool_name,tool_input
        return None,None




if __name__=="__main__":
    tool_executor=ToolExecutor()
    llm=HelloAgentsLLM()
    tool_executor.registerTool('Search','一个联网搜索工具',search)
    agent=react_agent(llm=llm,tool_executor=tool_executor)
    res=agent.run(question='苹果18什么时候发布的？')



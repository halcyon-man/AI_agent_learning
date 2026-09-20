
from llm_client import HelloAgentsLLM

PLANNER_PROMPT_TEMPLATE="""
定义：你是一名任务规划的领域的专家，给你数学问题，拆分成可执行的计算步骤。
要求：
1. 不要生成“整理已知条件、得出最终结果”这类纯描述步骤，只生成需要计算的操作。
2. 步骤粒度适中，一步只做一次计算。

问题：
{question}


请严格按照以下格式输出你的计划,```plan与```作为前后缀是必要的:
```plan['步骤1:内容','步骤2:内容','步骤3:内容'，...]```

"""

import ast
import llm_client
class Planner:
    def __init__(self, llm:HelloAgentsLLM):
        self.llm=llm

    def get_plan(self,question:str):

        prompt=PLANNER_PROMPT_TEMPLATE.format(
            question=question
        )
        messages=[{'role':'user','content':prompt}]
        response=self.llm.think(messages,temperature=0)
        if not response:
            print(f"llm解析失败")
            return []
        print(f"\n计划已经生成:{response}")
        try:
            plan_str=response.split("```plan")[1].split("```")[0].strip()

            plan_str=ast.literal_eval(plan_str)

            return plan_str
        except Exception as e:
            print(f'放生错误：{e}')
            return []

EXECUTOR_PROMPT_TEMPLATE="""
定义：你是分步执行任务的助手！
【硬性规则】
1. **只执行当前步骤，绝对不要提前执行后面任何步骤！**
2. 参考历史记录，历史记录是前面步骤已经算好的结果。
3. **只输出当前步骤的简短结果，禁止输出任何其他推理、禁止输出其他步骤！**
4. 不要预测后续步骤，不要一次性算出全部答案！

你要解决的问题：{question}

步骤为{plan}

历史记录为{history}

当前必须执行的步骤：{current_step}

只返回当前步骤的结果，不要多余文字：



"""



class Executor:

    def __init__(self,llm:HelloAgentsLLM):
        self.llm=llm

    def execute(self,question:str,plan:list):
        print(f'\n正在执行')
        history=''
        for i,item in enumerate(plan):
            print(f'\n执行第{i+1}/{len(plan)}步:{item}')
            prompt=EXECUTOR_PROMPT_TEMPLATE.format(question=question,plan=plan,history=history,current_step=item)
            message=[{'role':'user','content':prompt}]
            response=self.llm.think(message,temperature=0)
            history+=f"第{i+1}步|{item}|，结果是{response}\n"
            # print(f'\n第{i+1}/{len(plan)}的结果为{response}')

        return response


class PlanAndSolve:
    def __init__(self,executor:Executor,planner:Planner):
        self.executor=executor
        self.plan=planner
    def run(self,question:str):
        plan_1=self.plan.get_plan(question)
        response=self.executor.execute(question,plan_1)










if __name__=='__main__':
    llm=HelloAgentsLLM()
    planner=Planner(llm)
    question='"一个水果店周一卖出了15个苹果。周二卖出的苹果数量是周一的两倍。周三卖出的数量比周二少了5个。请问这三天总共卖出了多少个苹果？"'
    # plan=planner.get_plan(question)
    executor=Executor(llm)
    # executor.execute(question,plan)
    planandsolve=PlanAndSolve(executor,planner)
    res=planandsolve.run(question)

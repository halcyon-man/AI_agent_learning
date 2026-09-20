# Reflection Agent框架 案例
# 定义记忆容器
from typing import List, Dict, Any, Optional
from llm_client import HelloAgentsLLM


class Memory:

    def __init__(self):
        """
        初始化一个空列表，来记录历史信息
        """
        self.records:List[Dict[str,Any]] = []
    def add_record(self,record_type:str,record_content:Any):
        """
        添加推理过程
        """
        record = {'record_type':record_type,'record_content':record_content}
        self.records.append(record)



    def get_record(self):
        # 将列表记录转为字符串
        str_records=[str(item) for item in self.records]
        return '\n'.join(str_records)

    def clear_record(self):
        # 清空历史
        self.records=[]
        return self.records

class  LongTermMemory:

    def __init__(self):
        self.longtermmemory:List[Dict[str,Any]]=[]

    def save_memory(self,question:str,res:Any):
        self.longtermmemory.append({'question':question,'res':res})

    def get_long_memory(self):
        long_memory_str=[str(item) for item in self.longtermmemory]
        return '\n'.join(long_memory_str)



INPUT_PROMPT_TEMPLATE="""
定义：你是一名AI编程领域的专家，能根据问题给出相应的代码结果

问题：{question}

输出格式必须只输出结果的代码，不要带任何的形式，直接输出代码


"""






REFLECTION_PROMPT_TEMPLATE="""

定义：你是一名代码审核员，审核代码中的错误或者可以优化的地方


输出格式必须按照以下形式输出：原码和改进方案，如果不需要优化，直接输出不需要优化

原码为{current_code}

"""




REFINE_PROMPT_TEMPLATE="""
定义：你是一名资深的代码优化员，能够根据给出的原码和优化方案，对代码进行优化


原码：{raw_code}
改进方案：{reflection_content}

输出格式：
给出优化后的代码，不需要在添加任何东西，只要原码


"""

class Reflection:

    def __init__(self,memory:Memory,llm:HelloAgentsLLM,longtermmemory:LongTermMemory,max_trajectory=3):
        self.memory=memory
        self.llm=llm
        self.max_trajectory=max_trajectory
        self.longtermmemory=longtermmemory


    def run(self,question:str):
        # 调用run都清空历史记录

        self.memory.clear_record()
        prompt=INPUT_PROMPT_TEMPLATE.format(question=question)
        messages=[{'role':'user','content':prompt}]
        # 获取初步输出的结果
        initial_res=self.llm.think(messages=messages,temperature=0)
        self.memory.add_record(record_type='initial_res',record_content=initial_res)
        current_code=initial_res
        for i in range(self.max_trajectory):
            print(f'\n执行第{1+i}步\n')
            prompt=REFLECTION_PROMPT_TEMPLATE.format(current_code=current_code)
            messages=[{'role':'user','content':prompt}]
            # 获取反思的结果
            reflection_res=self.llm.think(messages=messages,temperature=0)
            self.memory.add_record(record_type='reflection_res',record_content=reflection_res)
            if "无需优化" in reflection_res or "没有错误" in reflection_res:
                print("✅ 反思判定代码已完善，提前终止迭代")
                break
            prompt=REFINE_PROMPT_TEMPLATE.format(raw_code=current_code,reflection_content=reflection_res)
            messages=[{'role':'user','content':prompt}]
            # 获取优化结果
            refine_res=self.llm.think(messages=messages,temperature=0)
            current_code = refine_res
            self.memory.add_record(record_type='refine_res',record_content=refine_res)
        self.longtermmemory.save_memory(question=question, res=current_code)
        print(f'\n执行结束，最后的结果如下：\n')
        print(current_code)


if __name__=="__main__":
    question="编写一个Python函数，找出1到n之间所有的素数 (prime numbers)。"
    memory=Memory()
    llm=HelloAgentsLLM()
    longtermmemory=LongTermMemory()
    reflection=Reflection(memory=memory,llm=llm,longtermmemory=longtermmemory)
    reflection.run(question=question)
    print(f'longtermmemory:{longtermmemory.get_long_memory()}')










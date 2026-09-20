import asyncio
# 异步编程
async def work(name, delay):
    print(f"{name}开始，等待{delay}秒")
    await asyncio.sleep(delay) # 模拟IO等待，不会阻塞
    print(f"{name}完成")

async def main():
    # 顺序执行（串行）
    await work("任务A", 2)
    await work("任务B", 2)
asyncio.run(main())
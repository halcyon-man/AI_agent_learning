# 第一个fastapi的程序
from fastapi import FastAPI

app = FastAPI()

@app.get("/")

def read_root():
    return {"Hello":"World"}

# 启动服务
# 1.通过命令：uvicorn main01:app --reload  # reload 自动加载我们更新的内容
# 2.通过调试：fastapi dev filename
# 3.通过py文件运行： python filename
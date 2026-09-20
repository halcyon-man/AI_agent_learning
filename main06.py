# 确定请求体的类型

from fastapi import FastAPI
from typing import Union,List

app = FastAPI()


# 路径参数只接受一个参数
@app.get("/item_id1/{item_id}")
def get_id(item_id: int):
    return {"item_id":item_id}

@app.get("/item_id2/{item_id}")
# 路径参数类型的声明，即限制参数类型
def get_id_1(item_id: Union[int,str]):
    return {"item_id":item_id}


@app.get("/item_id3")
def get_id_3(item_id:List):
    return {"item_id":item_id}

if __name__=="__main__":
    import uvicorn
    uvicorn.run("main06:app",host="127.0.0.1",port=8000,reload=True)


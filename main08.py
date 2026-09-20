#路径参数path
from fastapi import FastAPI,Path
from enum import  Enum
from typing import Annotated

from pydantic import BeforeValidator

app = FastAPI()


@app.get("/item1/{item_id}")
def read_item1(item_id:int):
    return {"item_id":item_id}


@app.get("/item2/{item_id}")
def read_item1(item_id:int=Path(...)):
    return {"item_id":item_id}


@app.get("/item3/{item_id}")
def read_item1(item_id:int=Path(...,gt=1,lt=100)):
    return {"item_id":item_id}

@app.get("/item4/{item_id}")
def read_item1(item_id:str=Path(...,regex=r"^d\d{2}$")):
    return {"item_id":item_id}

# 定义一个类，Enum随机
class ModelName(str,Enum):
    alexnet="ma"
    reset = "gaung"
    lenet = "yu"

@app.get("/item5/{model}")
def read_item1(model:ModelName):
    return {"model":model}

def validate(value):
    if not value.startswith("p-"):
        raise ValueError("必须以p-开头")
item = Annotated[str,BeforeValidator(validate)]



@app.get("/item6/{item_id}")
def read_item1(item_id:item):
    return {"item_id":item_id}




if __name__=="__main__":
    import uvicorn
    uvicorn.run("main08:app",host="127.0.0.1",port=8000,reload=True)
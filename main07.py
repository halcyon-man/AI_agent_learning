# Query请求参数验证
from fastapi import FastAPI,Query

app = FastAPI()

@app.get("/item1")
def read_id(item_id=Query(None)):
    return {"item_id":item_id}


@app.get("/item2")
def read_id(item_id:str = Query(...)):
    # Query(...)为必须传递
    return {"item_id":item_id}


@app.get("/item3")
def read_id(item_id:str = Query(...,min_length=3,max_length=10)):
    # Query(...)为必须传递，通过min和max来控制输入的长度
    return {"item_id":item_id}

@app.get("/item4")
def read_id(item_id:int = Query(...,get=1,lt=100)):
    # Query(...)为必须传递,限制内容大小
    return {"item_id":item_id}

@app.get("/item5")
def read_id(item_id:str = Query(...,alias="id")):
    """query（...）传递必须，修改名称"""
    return {"item_id":item_id}


@app.get("/item6")
def read_id(item_id:str = Query(...,description="这个是用来写你要查询的名称")):
    """query（...）传递必须，添加注释"""
    return {"item_id":item_id}


@app.get("/item7")
def read_id(item_id:str = Query(...,deprecated=True)):
    """query（...）传递必须，被抛弃了"""
    return {"item_id":item_id}


@app.get("/item8")
def read_id(item_id:str = Query(...,regex="^a\d{2}$")):
    """query（...）传递必须，规定输入的格式"""
    return {"item_id":item_id}
if __name__=="__main__":
    import uvicorn
    uvicorn.run("main07:app",host="127.0.0.1",port=8000,reload=True)
# 路径参数
from fastapi import FastAPI

app = FastAPI()

@app.get("/args/{item_id}")
def path_args(item_id:int):
    return {"message":f"您查询的商品id为{item_id}"}

if __name__=="__main__":
    import uvicorn
    uvicorn.run("main03:app",host="127.0.0.1",port=8000,reload=True )
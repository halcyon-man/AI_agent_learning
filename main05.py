# fastapi请求体
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class User(BaseModel):
    name:str
    age:int
    sex:str
    pwd:str

@app.post("/users")
def creat_users2(users:dict):

     return users

@app.post("/users2")
def creat_users(users:User):
    return users


if __name__=="__main__":
    import uvicorn
    uvicorn.run("main05:app",host="127.0.0.1",port=8001)
#File验证方式
from fastapi import FastAPI,Path
from pydantic import BaseModel,Field

app = FastAPI()

class User(BaseModel):
    name:str=Field(default="张三")
    age:int
    sex:str

@app.post("/user/")
def create_user(user:User):
    return user





if __name__=="__main__":
    import uvicorn
    uvicorn.run("main09:app",host="127.0.0.1",port=8000,reload=True)
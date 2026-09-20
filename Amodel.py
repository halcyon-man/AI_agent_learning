#路径参数path
from fastapi import FastAPI,Path

app = FastAPI()


if __name__=="__main__":
    import uvicorn
    uvicorn.run("main08:app",host="127.0.0.1",port=8000,reload=True)
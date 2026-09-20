from fastapi import FastAPI

app = FastAPI()

@app.get("/query1")
def query_limit(page:int,limit:int):
    return {"page":page,"limit":limit}

if __name__=="__main__":
    import uvicorn
    uvicorn.run("main04:app",host="127.0.0.1", reload=True)
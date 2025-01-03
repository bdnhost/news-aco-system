from fastapi import FastAPI

app = FastAPI(title="News-ACO-System API")

@app.get("/")
async def root():
    return {"status": "active"}

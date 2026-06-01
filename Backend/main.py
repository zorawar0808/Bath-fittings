from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hardware Store AI Backend Running"}
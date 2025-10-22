from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
def init():
    return {
        "code": 200,
        "message": "Success",
        }


if __name__ == "__main__":
    uvicorn.run(app="main:app", reload=True)

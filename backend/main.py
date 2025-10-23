from fastapi import FastAPI
from contextlib import asynccontextmanager
import uvicorn

from api_v1 import router
from core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(router=router, prefix=settings.api_v1_prefix)


@app.get("/")
def init():
    return {
        "code": 200,
        "message": "Success",
    }


if __name__ == "__main__":
    uvicorn.run(app="main:app", reload=True)

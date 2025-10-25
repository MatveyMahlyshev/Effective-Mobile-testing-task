from fastapi import FastAPI
from contextlib import asynccontextmanager
import uvicorn

from api_v1 import router
from core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    from create_admin import create_admin
    await create_admin()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(router=router, prefix=settings.api_v1_prefix)


if __name__ == "__main__":
    uvicorn.run(app="main:app")

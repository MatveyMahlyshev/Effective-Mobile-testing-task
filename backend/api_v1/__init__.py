from fastapi import APIRouter

from api_v1.users.views import main_router as users_router
from api_v1.auth.views import router as auth_router

router = APIRouter()
router.include_router(
    router=users_router,
    prefix="/users",
)
router.include_router(
    router=auth_router,
    prefix="/auth",
)

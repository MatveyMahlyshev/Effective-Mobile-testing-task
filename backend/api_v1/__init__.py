from fastapi import APIRouter

from api_v1.users.views import router as users_router
from api_v1.auth.views import router as auth_router
from api_v1.admin.views import router as admin_router
from api_v1.mock.views import router as mock_router

router = APIRouter()
router.include_router(router=mock_router, prefix="/mock-views")
router.include_router(
    router=users_router,
    prefix="/users",
)
router.include_router(
    router=auth_router,
    prefix="/auth",
)
router.include_router(
    router=admin_router,
    prefix="/admin",
)

from aiogram import Router

from .start import router as start_router
from .buy import router as buy_router
from .admin import router as admin_router

router = Router()
# include child routers once
router.include_router(start_router)
router.include_router(buy_router)
router.include_router(admin_router)

from aiogram import Router
from .start import router as start_router
from .buy import router as buy_router
from .topup import router as topup_router
from .admin import router as admin_router

router = Router()

# Routerlarni to‘g‘ri tartibda ulaymiz:
router.include_router(start_router)
router.include_router(buy_router)
router.include_router(topup_router)
router.include_router(admin_router)

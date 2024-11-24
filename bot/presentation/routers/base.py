from aiogram import Router

from bot.presentation.routers.chat import router


def get_all_routers() -> Router:
    base_router = Router()
    base_router.include_routers(router)
    return base_router

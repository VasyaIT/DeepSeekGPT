from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config.commands import set_bot_commands
from bot.config.config_bot import bot
from bot.presentation.routers.base import get_all_routers


async def main() -> None:
    """Entrypoint for start a bot"""

    dp = Dispatcher(storage=MemoryStorage())
    dp.include_routers(get_all_routers())
    await bot.delete_webhook(drop_pending_updates=True)
    await set_bot_commands(bot)
    await dp.start_polling(bot)

from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeChat, BotCommandScopeAllPrivateChats

from bot.config.config_bot import bot_config


class HandlerCommand:
    START = "start"
    NEW_CHAT = "new_chat"
    MY_CHATS = "my_chats"
    SUPPORT = "support"
    ADMIN = "admin"


async def set_bot_commands(bot: Bot) -> None:
    user_commands = [
        BotCommand(command=HandlerCommand.START, description="Главное меню"),
        BotCommand(command=HandlerCommand.NEW_CHAT, description="Добавить новый чат"),
        BotCommand(command=HandlerCommand.MY_CHATS, description="Все твои чаты"),
        BotCommand(command=HandlerCommand.SUPPORT, description="Тех. Поддержка"),
    ]
    await bot.set_my_commands(user_commands, BotCommandScopeAllPrivateChats())

    admin_commands = user_commands + [BotCommand(command=HandlerCommand.ADMIN, description="Админ панель")]
    for owner_id in bot_config.OWNERS_TELEGRAM_IDS:
        await bot.set_my_commands(admin_commands, BotCommandScopeChat(chat_id=owner_id))

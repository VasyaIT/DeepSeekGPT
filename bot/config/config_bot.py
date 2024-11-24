from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from pydantic_settings import BaseSettings


class BotConfig(BaseSettings):
    BOT_TOKEN: str
    OWNERS_TELEGRAM_IDS: list[int]
    AUTHORIZATION_TOKEN: str
    SUPPORT_USERNAME: str


bot_config = BotConfig()
bot = Bot(bot_config.BOT_TOKEN, default=DefaultBotProperties(parse_mode="html"))

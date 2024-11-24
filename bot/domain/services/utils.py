from bot.config.config_bot import bot, bot_config


async def send_to_owners(message: str, parse_mode: str | None = "html") -> None:
    for owner_id in bot_config.OWNERS_TELEGRAM_IDS:
        await bot.send_message(owner_id, message, parse_mode=parse_mode)

from bot.config.config_bot import bot_config

DEEPSEEK_API_URL = "https://chat.deepseek.com/api/v0"

REQUEST_HEADERS = {
    "authorization": f"Bearer {bot_config.AUTHORIZATION_TOKEN}",
    "content-type": "application/json",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "x-app-version": "20241018.0",
}

from traceback import format_exc, print_exc
from typing import Any, Awaitable, Callable, Sequence

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject, CallbackQuery
from aiogram.utils.markdown import hpre

from bot.domain.services.user import get_user
from bot.domain.services.utils import send_to_owners


class ChatTypeMiddleware(BaseMiddleware):
    def __init__(self, chat_types: Sequence[str]) -> None:
        self.chat_types = chat_types

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: dict[str, Any]
    ) -> Any:
        user = await get_user(event.from_user)
        if user.is_banned:
            return
        data["user"] = user

        try:
            chat_type = event.chat.type  # type: ignore
        except AttributeError:
            chat_type = event.message.chat.type  # type: ignore

        try:
            return await handler(event, data) if chat_type in self.chat_types else None
        except Exception:
            print_exc()
            message = f"{format_exc(chain=False)[:4096]}"
            await send_to_owners(hpre(message))

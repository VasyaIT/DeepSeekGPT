from bot.domain.const import DEFAULT_CHAT_TITLE
from bot.domain.dto.base import BaseDTO


class ChatDTO(BaseDTO):
    id: str
    user_id: int
    title: str = DEFAULT_CHAT_TITLE
    parent_message_id: int | None

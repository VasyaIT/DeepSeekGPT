from bot.domain.dto.base import BaseDTO


class UserDTO(BaseDTO):
    id: int
    username: str | None
    first_name: str | None
    is_banned: bool = False
    active_chat_id: str

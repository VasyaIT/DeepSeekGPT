from sqlalchemy import Boolean, String, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from bot.domain.models.base import Base


class User(Base):
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str | None] = mapped_column(String, nullable=True)
    first_name: Mapped[str | None] = mapped_column(String, nullable=True)
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False)
    active_chat_id: Mapped[str] = mapped_column(String)

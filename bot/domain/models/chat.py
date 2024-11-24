from sqlalchemy import Integer, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.domain.const import DEFAULT_CHAT_TITLE
from bot.domain.models.base import Base
from bot.domain.models.user import User


class Chat(Base):
    id: Mapped[str] = mapped_column(String, primary_key=True)
    title: Mapped[str] = mapped_column(String, default=DEFAULT_CHAT_TITLE)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    parent_message_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    user: Mapped[User] = relationship(User, lazy="selectin")

from typing import Sequence

from aiogram.types import User as TgUser
from sqlalchemy import insert, select, update

from bot.domain.dto.chat import ChatDTO
from bot.domain.dto.user import UserDTO
from bot.infrastructure.database.session import db_session
from bot.domain.models.chat import Chat
from bot.domain.models.user import User
from bot.infrastructure.deepseek.api import create_new_chat


async def get_user(tg_user: TgUser) -> UserDTO:
    """Get or create user"""

    stmt = select(User).filter_by(id=tg_user.id)
    async with db_session() as session:
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            chat_id = await create_new_chat()
            user_dto = UserDTO(
                id=tg_user.id, username=tg_user.username, first_name=tg_user.first_name, active_chat_id=chat_id
            )
            chat_dto = ChatDTO(id=chat_id, user_id=tg_user.id, parent_message_id=None)
            user_stmt = insert(User).values(user_dto.model_dump()).returning(User)
            chat_stmt = insert(Chat).values(chat_dto.model_dump())
            result = await session.execute(user_stmt)
            await session.execute(chat_stmt)
            await session.commit()
            user = result.scalar_one()

        return UserDTO(**user.__dict__)


async def update_user(user_id: int, **values) -> User | None:
    stmt = update(User).values(values).filter_by(id=user_id).returning(User)
    async with db_session() as session:
        result = await session.execute(stmt)
        await session.commit()
    return result.scalar_one_or_none()


async def get_all_users() -> Sequence[User]:
    stmt = select(User)
    async with db_session() as session:
        result = await session.execute(stmt)
    return result.scalars().all()

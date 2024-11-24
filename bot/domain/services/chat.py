from typing import Sequence
from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import IntegrityError

from bot.domain.dto.chat import ChatDTO
from bot.infrastructure.database.exceptions import AlreadyExistError
from bot.infrastructure.database.session import db_session
from bot.domain.models.chat import Chat


async def get_chat(chat_id: str) -> ChatDTO | None:
    stmt = select(Chat).filter_by(id=chat_id)
    async with db_session() as session:
        result = await session.execute(stmt)
    chat = result.scalar_one_or_none()
    if not chat:
        return

    return ChatDTO(**chat.__dict__)


async def update_chat(chat_id: str, **values) -> ChatDTO | None:
    stmt = update(Chat).values(values).filter_by(id=chat_id).returning(Chat)
    async with db_session() as session:
        result = await session.execute(stmt)
        await session.commit()
    chat = result.scalar_one_or_none()
    return ChatDTO(**chat.__dict__) if chat else None


async def create_chat(chat_dto) -> None:
    chat_stmt = insert(Chat).values(chat_dto.model_dump())
    async with db_session() as session:
        try:
            await session.execute(chat_stmt)
        except IntegrityError:
            raise AlreadyExistError("Empty chat already exist")
        await session.commit()


async def delete_chat(chat_id: str, user_id: int) -> None:
    chat_stmt = delete(Chat).filter_by(id=chat_id, user_id=user_id)
    async with db_session() as session:
        await session.execute(chat_stmt)
        await session.commit()


async def get_user_chats(**filters) -> Sequence[Chat]:
    chat_stmt = select(Chat).filter_by(**filters)
    async with db_session() as session:
        result = await session.execute(chat_stmt)
    return result.scalars().all()

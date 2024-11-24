from datetime import datetime, timedelta
from traceback import format_exc

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hpre

from bot.config.config_bot import bot_config
from bot.config.commands import HandlerCommand
from bot.domain.dto.chat import ChatDTO
from bot.domain.models.user import User
from bot.domain.services.chat import create_chat, delete_chat, get_chat, get_user_chats, update_chat
from bot.domain.services.user import get_all_users, update_user
from bot.domain.services.utils import send_to_owners
from bot.infrastructure.database.exceptions import AlreadyExistError
from bot.infrastructure.deepseek.api import create_new_chat, delete_chat_session, generate_answer
from bot.presentation.keyboards.chat import back_kb, chats_kb, edit_chat_kb
from bot.presentation.middlewares.chat_type import ChatTypeMiddleware
from bot.presentation.states.chat import AddChatState, EditChatState


router = Router()
router.message.middleware.register(ChatTypeMiddleware(("private")))
router.callback_query.middleware.register(ChatTypeMiddleware(("private")))


@router.message(Command(HandlerCommand.START))
async def start_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "<b>Привет!</b>\n\nКто угодно может спросить меня о чём угодно - <b>Я знаю всё, отвечу на любой твой вопрос</b>"
    )


@router.message(Command(HandlerCommand.NEW_CHAT))
async def new_chat_handler(message: Message, state: FSMContext) -> None:
    await state.set_state(AddChatState.title)
    await message.answer("Отправь название для нового чата", reply_markup=back_kb())


@router.message(Command(HandlerCommand.MY_CHATS))
async def my_chats_handler(message: Message, state: FSMContext, user: User) -> None:
    await state.clear()
    chats = await get_user_chats(user_id=user.id)
    await message.answer(
        "Ниже представлены твои чаты\n\n<i>Текущий активный чат помечен - ✅</i>",
        reply_markup=chats_kb(list(chats), user.active_chat_id)
    )


@router.message(Command(HandlerCommand.SUPPORT))
async def support_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(f"По вопросам вопросов писать сюда - <b>{bot_config.SUPPORT_USERNAME}</b>")


@router.message(Command(HandlerCommand.ADMIN))
async def admin_handler(message: Message, user: User) -> None:
    if user.id not in bot_config.OWNERS_TELEGRAM_IDS:
        return

    all_users = await get_all_users()
    answer = f"Количество пользователей: {len(all_users)}\n"
    for user in all_users:
        answer += f"\n<code>{user.id}</code> - @{user.username}"

    await message.answer(answer)


@router.message(F.text, EditChatState.title)
async def edit_chat_title_handler(message: Message, state: FSMContext, user: User) -> Message | None:
    chat_id = await state.get_value("chat_id", "")
    chat_dto = await update_chat(chat_id=chat_id, title=message.text, user_id=user.id)
    if not chat_dto:
        return await message.answer(
            "Не удалось изменить название, попробуй ещё раз\n\n"
            f"<i>Если ошибка повторится, обратись в поддержку - {bot_config.SUPPORT_USERNAME}</i>"
        )
    await message.answer(
        "✅ <b>Название успешно изменено!</b>"
        f"\n\n<i>Для просмотра и редактирования чатов отправь команду</i> /{HandlerCommand.MY_CHATS}",
        reply_markup=back_kb()
    )
    await state.clear()


@router.message(F.text, AddChatState.title)
async def get_chat_title_handler(message: Message, state: FSMContext, user: User) -> Message | None:
    if await get_user_chats(parent_message_id=None):
        return await message.answer(
            "У тебя есть пустой неиспользованный чат\nНачни диалог там, чтобы было доступно создание нового",
            reply_markup=back_kb()
        )

    try:
        chat_id = await create_new_chat()
    except Exception:
        await send_to_owners(hpre(f"API ERROR [create chat]: {format_exc(chain=False)[:4000]}"))
        return await message.answer(
            "Не удалось добавить новый чат, попробуй ещё раз\n\n"
            f"<i>Если ошибка повторится, обратись в поддержку - {bot_config.SUPPORT_USERNAME}</i>"
        )

    await create_chat(ChatDTO(id=chat_id, user_id=user.id, title=message.text, parent_message_id=None))
    await update_user(user.id, active_chat_id=chat_id)
    await message.answer(
        "✅ <b>Новый чат успешно добавлен!</b>"
        f"\n\n<i>Для просмотра и редактирования чатов отправь команду</i> /{HandlerCommand.MY_CHATS}"
    )
    await state.clear()


@router.message(F.text)
async def prompt_handler(message: Message, state: FSMContext, user: User) -> Message | None:
    chat = await get_chat(user.active_chat_id)
    if not chat:
        return
    request_expire_at = await state.get_value("request_expire_at")
    if request_expire_at:
        if datetime.now() < request_expire_at:
            return await message.answer("☝️ Обожди, у тебя уже есть активный запрос!")
        await state.clear()
    bot_message = await message.answer("Запрос в обработке...")
    await state.update_data(request_expire_at=datetime.now() + timedelta(minutes=1))
    try:
        answer, next_parent_message_id = await generate_answer(
            prompt=message.text, chat_id=chat.id, parent_message_id=chat.parent_message_id
        )
    except Exception:
        await send_to_owners(hpre(f"API ERROR: {format_exc(chain=False)[:4000]}"))
        await state.clear()
        return await message.answer(
            "Ошибка при генерации ответа, попробуй ещё раз\n\n"
            f"<i>Если ошибка повторится, обратись в поддержку - {bot_config.SUPPORT_USERNAME}</i>"
        )
    await state.clear()
    await bot_message.delete()
    await message.answer(answer, parse_mode="markdown")
    await update_chat(chat_id=chat.id, parent_message_id=next_parent_message_id)


@router.callback_query(F.data == "create_chat")
async def new_chat_callback(call: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AddChatState.title)
    await call.message.edit_text("Отправь название для нового чата", reply_markup=back_kb())


@router.callback_query(F.data.startswith("chat:"))
async def edit_chat(call: CallbackQuery, state: FSMContext, user: User) -> Message | bool | None:
    await state.clear()
    chat_id = call.data.replace("chat:", "")
    chat_dto = await get_chat(chat_id)
    if not chat_dto:
        return await call.message.edit_text(
            f"Чат не найден.\nПожалуйста, обратись в поддержку - {bot_config.SUPPORT_USERNAME}"
        )
    is_active = user.active_chat_id == chat_id
    is_active_text = "✅ Активен" if is_active else "❌ Неактивен"
    await call.message.edit_text(
        f"<b>{chat_dto.title}</b> - {is_active_text}", reply_markup=edit_chat_kb(chat_id, is_active)
    )


@router.callback_query(F.data == "chats")
async def my_chats_callback(call: CallbackQuery, state: FSMContext, user: User, text_args: str = "") -> None:
    await state.clear()
    chats = await get_user_chats(user_id=user.id)
    await call.message.edit_text(
        f"{text_args}Ниже представлены твои чаты\n\n<i>Текущий активный чат помечен - ✅</i>",
        reply_markup=chats_kb(list(chats), user.active_chat_id)
    )


@router.callback_query(F.data.startswith("rename_chat:"))
async def rename_chat_callback(call: CallbackQuery, state: FSMContext) -> Message | bool | None:
    chat_id = call.data.replace("rename_chat:", "")
    await state.set_state(EditChatState.title)
    await state.update_data(chat_id=chat_id)
    await call.message.edit_text("Отправь новое название для чата", reply_markup=back_kb(f"chat:{chat_id}"))


@router.callback_query(F.data.startswith("activate_chat:"))
async def activate_chat_callback(call: CallbackQuery, state: FSMContext, user: User) -> Message | bool | None:
    chat_id = call.data.replace("activate_chat:", "")
    updated_user = await update_user(user.id, active_chat_id=chat_id)
    if not updated_user:
        return
    await my_chats_callback(call, state, updated_user)


@router.callback_query(F.data.startswith("delete_chat:"))
async def delete_chat_callback(call: CallbackQuery, state: FSMContext, user: User) -> Message | bool | None:
    chat_id = call.data.replace("delete_chat:", "")
    try:
        await delete_chat_session(chat_id)
    except Exception:
        await send_to_owners(hpre(f"API ERROR: {format_exc(chain=False)[:4000]}"))
        await state.clear()
        return
    await delete_chat(chat_id, user.id)
    await my_chats_callback(call, state, user, "✅ <b>Чат успешно удалён</b>\n\n")

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.domain.models.chat import Chat


def chats_kb(chats: list[Chat], active_chat_id: str) -> InlineKeyboardMarkup:
    keyboard, add_chat_builder = InlineKeyboardBuilder(), InlineKeyboardBuilder()
    keyboard.max_width = 2
    add_chat_builder.row(InlineKeyboardButton(text="➕ Добавить чат", callback_data=f"create_chat"))
    for chat in chats:
        emoji = "✅ " if active_chat_id == chat.id else ""
        keyboard.button(text=f"{emoji}{chat.title}", callback_data=f"chat:{chat.id}")

    add_chat_builder.attach(keyboard)
    return add_chat_builder.as_markup()


def edit_chat_kb(chat_id: str, is_active: bool) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    if not is_active:
        keyboard.row(InlineKeyboardButton(text="🔁 Сделать активным", callback_data=f"activate_chat:{chat_id}"))
        keyboard.row(
            InlineKeyboardButton(text="📝 Изменить название", callback_data=f"rename_chat:{chat_id}"),
            InlineKeyboardButton(text="🗑️ Удалить", callback_data=f"delete_chat:{chat_id}"),
        )
    else:
        keyboard.row(
            InlineKeyboardButton(text="📝 Изменить название", callback_data=f"rename_chat:{chat_id}")
        )

    keyboard.row(InlineKeyboardButton(text="Назад", callback_data="chats"))

    return keyboard.as_markup()


def back_kb(callback: str = "chats") -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text="Назад", callback_data=callback))
    return keyboard.as_markup()

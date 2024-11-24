from aiogram.fsm.state import StatesGroup, State


class AddChatState(StatesGroup):
    title = State()


class EditChatState(StatesGroup):
    title = State()

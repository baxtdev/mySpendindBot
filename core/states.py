from aiogram.filters.state import State, StatesGroup
from aiogram.types import DateTime

class TaskStates(StatesGroup):
    name = State()
    date = State()
    category = State()
    amount = State()

    
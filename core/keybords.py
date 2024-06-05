from aiogram.types import InlineKeyboardButton, \
    InlineKeyboardMarkup, KeyboardButton,\
    ReplyKeyboardMarkup, ReplyKeyboardRemove


menu = [
    [InlineKeyboardButton(text="📝 Добавит Траты", callback_data="add_expence"),InlineKeyboardButton(text="📝 Мои расходы", callback_data="myexpences"),]
]




def create_task_menu(task_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Изменить Задачу", callback_data=f"edit_task:{task_id}"),
        InlineKeyboardButton(text="📝 Удалить Задачу", callback_data=f"del_task:{task_id}")]
    ])

menu = InlineKeyboardMarkup(inline_keyboard=menu)

exit_kb = ReplyKeyboardMarkup(keyboard=[
    [
    KeyboardButton(text="Menu",)
    ]
    ], resize_keyboard=True)

iexit_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Выйти в меню", callback_data="menu")]])

import logging
from datetime import date
from aiogram import F, Router, types, html
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.enums.parse_mode import ParseMode
from typing import Any, Dict
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback
from pydantic import ValidationError
from core.models import TaskModel
from core import keybords as kb
from core import texts as text
from core import utils
from core.states import TaskStates
from core.db import create_task, get_tasks, delete_task,get_summ
from core.request.main import get

router = Router()



@router.message(Command(commands=["start","hello"]))
async def start_handler(msg: Message):  
    await msg.answer(
        f"Привет! <b>{html.quote(msg.from_user.username)}</b> я бот для запис расходот, могу сохранить твои расходы",
        parse_mode=ParseMode.HTML,
        reply_markup=kb.menu,
    )


@router.message(Command("menu"))
async def menu_handler(msg: Message):
    await msg.answer(text.menu, reply_markup=kb.menu, parse_mode=ParseMode.HTML)


@router.message(Command(commands=["seumm","summary","all"]))
async def summary_handler(msg: Message):
    data = await get_summ(msg.from_user.id)
    await msg.answer(text=f"Сумма ваших трат {data}", reply_markup=kb.menu, parse_mode=ParseMode.HTML)


@router.callback_query(F.data == "myexpences")
async def my_task_handler(clbck: types.CallbackQuery):
    tasks = await get_tasks(clbck.from_user.id)
    for task in tasks:
        task_text = (
            f"📋 <b>Название:</b> {html.quote(task['name'])}\n\n"
            f"📅 <b>Дата:</b> {html.quote(task['date'])}\n\n"
            f"⏰ <b>Сумма:</b> {html.quote(task['amount'])}\n\n"
            f"⏰ <b>Категория:</b> {html.quote(task['category'])}\n\n"
        )
        await clbck.message.answer(text=task_text, parse_mode=ParseMode.HTML,reply_markup=kb.menu)
    
    await clbck.answer("Это все")




@router.callback_query(F.data == "add_expence")
async def add_task_handler(clbck: types.CallbackQuery, state: FSMContext):
    await state.set_state(TaskStates.name)
    await clbck.answer("Введите название задачи")
    await clbck.message.answer(
        "Введите название задачи",
        reply_markup=kb.ReplyKeyboardMarkup(
            keyboard=[[kb.KeyboardButton(text="cancel")]],
            resize_keyboard=True,
        ),
    )


@router.message(Command("cancel"))
@router.message(F.text.casefold() == "cancel")
async def cancel_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info("Cancelling state %r", current_state)
    await state.clear()
    await message.answer(
        "Cancelled.",
        reply_markup=kb.ReplyKeyboardRemove()
    )


@router.message(TaskStates.name)
async def process_name(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text)
    await state.set_state(TaskStates.date)
    data = await state.get_data()
    await message.reply(
        f"Имя задачи сохранено: {html.quote(data['name'])}\nВведите дату начала",
        reply_markup=await SimpleCalendar().start_calendar()
    )


@router.callback_query(SimpleCalendarCallback.filter())
async def process_calendar(callback_query: types.CallbackQuery, callback_data: dict, state: FSMContext):
    selected, selected_date = await SimpleCalendar().process_selection(callback_query, callback_data)
    if selected:
        await state.update_data(date=selected_date.isoformat())
        data = await state.get_data()

        await  callback_query.message.reply(
        f"Дата задачи сохранено: {html.quote(data['date'])}\nВыберите категорию ",
        reply_markup=kb.ReplyKeyboardMarkup(
            keyboard=[[kb.KeyboardButton(text="cancel"),kb.KeyboardButton(text="Кушать")]],
            resize_keyboard=True,
        ),
        )
        await state.set_state(TaskStates.category)


@router.message(TaskStates.category)
async def process_category(message: Message, state: FSMContext) -> None:
    await state.update_data(category=message.text)
    await state.set_state(TaskStates.amount)
    data = await state.get_data()
    await message.reply(
        f"Категория задачи сохранено: {html.quote(data['category'])}\nВведите сумму",
        reply_markup=kb.ReplyKeyboardMarkup(
            keyboard=[[kb.KeyboardButton(text="cancel")]],
            resize_keyboard=True,
            )
        )
    

@router.message(TaskStates.amount)
async def process_amount(message: Message, state: FSMContext) -> None:
    await state.update_data(amount=message.text)
    data = await state.get_data()
    
    await message.reply(
        f"Сумма задачи сохранено: {data}\nВведите описание",
        )
    
    
    await show_summary(message=message, data=data)


async def show_summary(message: Message, data: Dict[str, Any], positive: bool = True) -> None:
    user_data = data
    user_data["user_id"] = message.from_user.id
    await create_task(user_data)
    
    task_text = (
            f"📋 <b>Название:</b> {html.quote(user_data['name'])}\n\n"
            f"📅 <b>Дата:</b> {html.quote(user_data['date'])}\n\n"
            f"⏰ <b>Категория:</b> {html.quote(user_data['category'])}\n\n"
            f"⏰ <b>Сумма:</b> {html.quote(user_data['amount'])}\n\n"
        )

    await message.answer(text=task_text, reply_markup=kb.ReplyKeyboardMarkup(
            keyboard=[[kb.KeyboardButton(text="/menu")]],
            resize_keyboard=True,
        ),)

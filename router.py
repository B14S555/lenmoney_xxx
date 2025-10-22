import asyncio
from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
import kb
import bd.reqest as db

router = Router()

# FSM состояния
class AddRecord(StatesGroup):
    amount = State()
    description = State()
    type = State()

# Быстрый ответ Telegram
async def safe_answer(callback: CallbackQuery):
    try:
        await callback.answer()
    except:
        pass

# Логирование действий
def log_action(user, action: str):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 👤 {user.full_name} ({user.id}): {action}")

# === /start ===
@router.message(CommandStart())
async def start(message: Message):
    log_action(message.from_user, "запустил бота")
    await message.answer("Привет! 🐼 Я — MoneyPanda, твоя личная финансовая панда 💚  ", reply_markup=kb.main_menu)

# === Расход ===
@router.callback_query(F.data == "add_expense")
async def add_expense(callback: CallbackQuery, state: FSMContext):
    asyncio.create_task(safe_answer(callback))
    log_action(callback.from_user, "начал добавление расхода")
    await state.set_state(AddRecord.amount)
    await state.update_data(type="expense")
    await callback.message.answer("💸 Введите сумму расхода:", reply_markup=kb.exit)

# === Прибыль ===
@router.callback_query(F.data == "add_profit")
async def add_profit(callback: CallbackQuery, state: FSMContext):
    asyncio.create_task(safe_answer(callback))
    log_action(callback.from_user, "начал добавление прибыли")
    await state.set_state(AddRecord.amount)
    await state.update_data(type="profit")
    await callback.message.answer("📈 Введите сумму прибыли:", reply_markup=kb.exit)

# === Ввод суммы ===
@router.message(AddRecord.amount)
async def enter_sum(message: Message, state: FSMContext):
    try:
        amount = int(message.text)
        await state.update_data(amount=amount)
        await state.set_state(AddRecord.description)
        log_action(message.from_user, f"ввел сумму: {amount}")
        await message.answer("📝 Введите описание:", reply_markup=kb.exit)
    except ValueError:
        await message.answer("⚠️ Введите число, например 250")

# === Ввод описания и запись ===
@router.message(AddRecord.description)
async def enter_description(message: Message, state: FSMContext):
    data = await state.get_data()
    data["description"] = message.text

    await db.add_record(message.from_user.id, data)
    emoji = "📉" if data["type"] == "expense" else "📈"
    log_action(message.from_user, f"добавил запись: {emoji} {data['amount']} грн — {data['description']}")

    await message.answer(
        f"{emoji} Запись добавлена!\n💰 {data['amount']} грн\n📝 {data['description']}",
        reply_markup=kb.main_menu
    )
    await state.clear()

# === Последние операции ===
@router.callback_query(F.data == "stats")
async def stats(callback: CallbackQuery):
    asyncio.create_task(safe_answer(callback))
    log_action(callback.from_user, "просмотрел последние операции")
    text = await db.get_last_records(callback.from_user.id)
    await callback.message.answer(text, parse_mode="HTML", reply_markup=kb.main_menu)

# === Баланс ===
@router.callback_query(F.data == "balance")
async def balance(callback: CallbackQuery):
    asyncio.create_task(safe_answer(callback))
    log_action(callback.from_user, "запросил общий баланс")
    text = await db.get_statistics(callback.from_user.id)
    await callback.message.answer(text, parse_mode="HTML", reply_markup=kb.main_menu)

# === Месячный отчет ===
@router.callback_query(F.data == "monthly_report")
async def monthly_report(callback: CallbackQuery):
    asyncio.create_task(safe_answer(callback))
    log_action(callback.from_user, "запросил месячный отчет")
    text = await db.get_monthly_report(callback.from_user.id)
    await callback.message.answer(text, parse_mode="HTML", reply_markup=kb.main_menu)

# === Выход в меню ===
@router.callback_query(F.data == "exit")
async def exit_menu(callback: CallbackQuery, state: FSMContext):
    asyncio.create_task(safe_answer(callback))
    log_action(callback.from_user, "вернулся в меню")
    await state.clear()
    await callback.message.answer("🏠 Главное меню:", reply_markup=kb.main_menu)

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# months mapping (if needed elsewhere)
months = {
    1: 'Январь',
    2: 'Февраль',
    3: 'Март',
    4: 'Апрель',
    5: 'Май',
    6: 'Июнь',
    7: 'Июль',
    8: 'Август',
    9: 'Сентябрь',
    10: 'Октябрь',
    11: 'Ноябрь',
    12: 'Декабрь',
}

# main menu — вариант 3: группы
main_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="💸 Добавить расход", callback_data="add_expense")],
    [InlineKeyboardButton(text="📈 Добавить прибыль", callback_data="add_profit")],
    [InlineKeyboardButton(text="📊 Статистика", callback_data="stats")],
    [InlineKeyboardButton(text="💰 Баланс", callback_data="balance")],
    [InlineKeyboardButton(text="📆 Отчёт по месяцам", callback_data="monthly_report")]
])

exit = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="⬅️ Назад", callback_data="exit")]
])

def getYearsButton(years):
    buttons = [[InlineKeyboardButton(text=str(i), callback_data=f"year:{i}") ] for i in years]
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="exit")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def getMonths():
    buttons = []
    for i in range(1, 13):
        buttons.append([InlineKeyboardButton(text=f"{i}", callback_data=f"month:{i}")])
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="exit")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

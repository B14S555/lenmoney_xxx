from datetime import datetime
from calendar import monthrange
from sqlalchemy import select, and_, func
from bd.models import async_session, Expense

# ======================
# Добавление записи (расход или прибыль)
# ======================
async def add_record(user_id: int, data: dict):
    amount = data.get("amount")
    description = data.get("description", "-")
    rec_type = data.get("type", "expense")  # expense / profit

    now = datetime.now()
    async with async_session() as session:
        record = Expense(
            user_id=user_id,
            amount=amount,
            description=description,
            type=rec_type,
            year=now.year,
            month=now.month,
            day=now.day
        )
        session.add(record)
        await session.commit()

# ======================
# Последние операции
# ======================
async def get_last_records(user_id: int, limit: int = 10) -> str:
    async with async_session() as session:
        q = (
            select(Expense)
            .where(Expense.user_id == user_id)
            .order_by(Expense.id.desc())
            .limit(limit)
        )
        res = await session.scalars(q)
        rows = res.all()

    if not rows:
        return "📭 У вас пока нет записей."

    lines = ["📋 <b>Последние операции:</b>\n"]
    for rec in rows:
        sign = "➕" if rec.type == "profit" else "➖"
        emoji = "💰" if rec.type == "profit" else "💸"
        lines.append(f"{emoji} {sign}{rec.amount} грн — {rec.description} ({rec.day:02d}.{rec.month:02d}.{rec.year})")

    return "\n".join(lines)

# ======================
# Общая статистика (баланс)
# ======================
async def get_statistics(user_id: int) -> str:
    async with async_session() as session:
        profit_q = select(func.coalesce(func.sum(Expense.amount), 0)).where(
            and_(Expense.user_id == user_id, Expense.type == "profit")
        )
        expense_q = select(func.coalesce(func.sum(Expense.amount), 0)).where(
            and_(Expense.user_id == user_id, Expense.type == "expense")
        )

        profit = await session.scalar(profit_q) or 0
        expense = await session.scalar(expense_q) or 0
        balance = profit - expense

    emoji = "🟢" if balance >= 0 else "🔴"
    return (
        f"📊 <b>Ваша статистика</b>\n\n"
        f"📈 Прибыль: <b>{profit}</b> грн\n"
        f"📉 Расходы: <b>{expense}</b> грн\n\n"
        f"{emoji} Баланс: <b>{balance}</b> грн"
    )

# ======================
# Месячный отчёт
# ======================
async def get_monthly_report(user_id: int) -> str:
    now = datetime.now()
    start = datetime(now.year, now.month, 1)
    end = datetime(now.year, now.month, monthrange(now.year, now.month)[1], 23, 59, 59)

    async with async_session() as session:
        q = select(Expense).where(
            and_(
                Expense.user_id == user_id,
                Expense.year == now.year,
                Expense.month == now.month
            )
        ).order_by(Expense.day)
        res = await session.scalars(q)
        rows = res.all()

    if not rows:
        return "📭 В этом месяце нет записей."

    total_profit = sum(r.amount for r in rows if r.type == "profit")
    total_expense = sum(r.amount for r in rows if r.type == "expense")
    balance = total_profit - total_expense

    lines = [f"📆 <b>Отчёт за {now.month:02d}.{now.year}</b>\n"]
    for rec in rows:
        sign = "➕" if rec.type == "profit" else "➖"
        emoji = "💰" if rec.type == "profit" else "💸"
        lines.append(f"{emoji} {sign}{rec.amount} грн — {rec.description} ({rec.day:02d})")

    lines.append("\n──────────────")
    lines.append(f"📈 Прибыль: <b>{total_profit}</b> грн")
    lines.append(f"📉 Расходы: <b>{total_expense}</b> грн")
    lines.append(f"💬 Баланс: <b>{balance}</b> грн")

    return "\n".join(lines)

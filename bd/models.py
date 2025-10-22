from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import String, Integer
import os

# ======================
# Путь к базе
# ======================
os.makedirs("/data", exist_ok=True)
DATABASE_URL = "sqlite+aiosqlite:////data/database.db"

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

# ======================
# Модель расходов/прибыли
# ======================
class Expense(Base):
    __tablename__ = "money"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer)
    amount: Mapped[int] = mapped_column(Integer)
    description: Mapped[str] = mapped_column(String(255))
    type: Mapped[str] = mapped_column(String(10))  # <== ВАЖНО (expense / profit)
    year: Mapped[int] = mapped_column(Integer)
    month: Mapped[int] = mapped_column(Integer)
    day: Mapped[int] = mapped_column(Integer)

# ======================
# Инициализация базы
# ======================
async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


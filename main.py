import os
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from router import router  # импорт твоего router.py
from bd.models import async_main  # чтобы создать таблицы

TOKEN = os.getenv("8445908325:AAG191sQXcg-BhZDibV3FYCnXSopNAKdCTM")
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}{WEBHOOK_PATH}"

bot = Bot(token=TOKEN)
dp = Dispatcher()
dp.include_router(router)

async def on_startup(app):
    print("🔹 Starting bot...")
    await async_main()  # создаём таблицы, если нет
    await bot.set_webhook(WEBHOOK_URL)
    print(f"✅ Webhook set to: {WEBHOOK_URL}")

async def on_shutdown(app):
    print("🔻 Shutting down bot...")
    await bot.delete_webhook()
    await bot.session.close()

async def create_app():
    app = web.Application()
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)

    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    return app

if __name__ == "__main__":
    web.run_app(create_app(), host="0.0.0.0", port=int(os.getenv("PORT", 8080)))

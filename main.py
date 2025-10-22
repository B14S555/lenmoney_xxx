import os
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from router import router
from bd.models import async_main

BOT_TOKEN = "8445908325:AAG191sQXcg-BhZDibV3FYCnXSopNAKdCTM"  # ← вставь токен сюда руками
import os
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from router import router
from bd.models import async_main
import asyncio

os.makedirs("/data", exist_ok=True)
# 🔑 Укажи токен бота напрямую, без secrets
BOT_TOKEN = "8445908325:AAG191sQXcg-BhZDibV3FYCnXSopNAKdCTM"

WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"https://{os.getenv('FLY_APP_NAME')}.fly.dev{WEBHOOK_PATH}"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
dp.include_router(router)


async def on_startup(app: web.Application):
    await async_main()
    await bot.delete_webhook(drop_pending_updates=True)  # 💥 очистка старых апдейтов
    await asyncio.sleep(2)  # ← пауза для стабильного старта
    await bot.set_webhook(WEBHOOK_URL)
    print(f"✅ Webhook установлен: {WEBHOOK_URL}")

async def on_shutdown(app: web.Application):
    await bot.delete_webhook()
    await bot.session.close()
    print("🛑 Webhook удалён, бот остановлен")

async def webhook_handler(request: web.Request):
    update = await request.json()
    await dp.feed_webhook_update(bot, update)
    return web.Response()

def main():
    app = web.Application()
    app.router.add_post(WEBHOOK_PATH, webhook_handler)
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    setup_application(app, dp, bot=bot)

    # 👇 ОБЯЗАТЕЛЬНО 0.0.0.0 и порт 8080
    web.run_app(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))

if __name__ == "__main__":
    main()
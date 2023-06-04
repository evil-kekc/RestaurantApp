import logging
import os

from aiogram import Bot
from aiogram import types, Dispatcher
from aiogram.types import BotCommand
from aiogram.utils.exceptions import BadRequest
from fastapi import FastAPI

from config.bot_config import bot, dp, LOGGER, TOKEN
from handlers.common import register_handlers_common
from handlers.registration.registration import register_handlers_registration

BASE_DIR = os.path.abspath(os.path.curdir)

logging.basicConfig(level=logging.INFO, filename=fr"{str(BASE_DIR)}/{LOGGER}",
                    format="%(asctime)s | %(levelname)s | %(funcName)s: %(lineno)d | %(message)s",
                    datefmt="%H:%M:%S")

app = FastAPI()
# templates = Jinja2Templates(directory=fr"{BASE_DIR}/app/templates")

WEBHOOK_PATH = f"/bot/{TOKEN}"
WEBHOOK_URL = os.getenv('HOST_URL') + WEBHOOK_PATH


async def set_commands(bot_: Bot):
    """Creating a bot menu

    :param bot_: an instance of the bot class
    :return:
    """
    commands = [
        BotCommand(command='/start', description='Начало работы'),
    ]

    await bot_.set_my_commands(commands)


async def bot_main():
    """Bot launch

    :return: None
    """
    logging.info('Starting bot')
    register_handlers_registration(dp)
    register_handlers_common(dp)

    await set_commands(bot)


@app.on_event("startup")
async def on_startup():
    """Setting up a webhook

    :return:
    """
    try:
        webhook_info = await bot.get_webhook_info()
        if webhook_info.url != WEBHOOK_URL:
            await bot.set_webhook(
                url=WEBHOOK_URL,
                drop_pending_updates=True
            )
    except BadRequest as ex:
        if "ip address 127.0.0.1 is reserved" in str(ex):
            logging.error('ip address 127.0.0.1 is reserved')
        else:
            logging.error(repr(ex))


@app.post(WEBHOOK_PATH)
async def bot_webhook(update: dict):
    """Getting Telegram updates

    :param update: Telegram update
    :return:
    """
    try:
        telegram_update = types.Update(**update)
        Dispatcher.set_current(dp)
        Bot.set_current(bot)
        await bot_main()
        await dp.process_update(telegram_update)
    except Exception as ex:
        logging.error(repr(ex))


@app.on_event("shutdown")
async def on_shutdown():
    """Closing session and delete webhook

    :return:
    """
    await dp.storage.close()
    await dp.storage.wait_closed()
    await bot.session.close()
    await bot.delete_webhook()

import logging

from dotenv import load_dotenv

from .config import Settings
from .telegram_bot import TelegramBot


def main() -> None:
    load_dotenv()
    settings = Settings()
    settings.validate()

    logging.basicConfig(level=getattr(logging, settings.log_level, logging.INFO))

    bot = TelegramBot(settings)
    app = bot.build_app()

    # python-telegram-bot runs its own asyncio loop internally here.
    app.run_polling(allowed_updates=None)


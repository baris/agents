import asyncio
import logging
import signal
import sys
from typing import Any

from src.bot import TelegramBridgeBot
from src.config import load_settings
from src.logger import get_logger, setup_logging

logger = get_logger("main")


async def shutdown(bot: TelegramBridgeBot, sig: Any) -> None:
    """Gracefully shuts down the bot daemon on receipt of signal."""
    logger.info("Received exit signal %s, stopping bridge...", sig.name)
    await bot.stop()
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    for task in tasks:
        task.cancel()
    logger.info("Shutdown completed.")
    loop = asyncio.get_running_loop()
    loop.stop()


def setup_signal_handlers(bot: TelegramBridgeBot) -> None:
    """Binds SIGINT and SIGTERM handler callback functions."""
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        def handle_sig(s: signal.Signals = sig) -> None:
            asyncio.create_task(shutdown(bot, s))
        try:
            loop.add_signal_handler(sig, handle_sig)
        except NotImplementedError:
            # Handles systems where add_signal_handler is not implemented (e.g. Windows)
            pass


async def main() -> None:
    """Prepares and bootstraps the main application daemon loop."""
    setup_logging(logging.INFO)
    logger.info("Initializing Telegram Remote Control Bridge...")

    try:
        settings = load_settings()
    except Exception as e:
        logger.critical("Configuration failure: %s", e, exc_info=True)
        sys.exit(1)

    bot = TelegramBridgeBot(settings)
    setup_signal_handlers(bot)

    try:
        await bot.start()
        # Keep the main process alive
        while True:
            await asyncio.sleep(3600)
    except asyncio.CancelledError:
        pass
    except Exception as e:
        logger.critical("Daemon crashed: %s", e, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass

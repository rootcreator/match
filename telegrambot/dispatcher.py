import logging
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    Application
)
from .handlers.start import start
from .handlers.predict import predict_command
from .handlers.nextmatch import nextmatch
from .handlers.text import handle_text
from .handlers.inline import inline_handler

logger = logging.getLogger(__name__)

def setup_application(app: Application) -> None:
    """Register all handlers with proper error handling."""
    try:
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("predict", predict_command))
        app.add_handler(CommandHandler("nextmatch", nextmatch))

        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
        app.add_handler(CallbackQueryHandler(inline_handler))

        logger.info("All handlers registered successfully")
    except Exception as e:
        logger.error(f"Failed to setup handlers: {e}")
        raise
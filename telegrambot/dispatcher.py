from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, filters
from .handlers.start import start
from .handlers.predict import predict_command, nextmatch
from .handlers.text import handle_text
from .handlers.inline import inline_handler

def setup_dispatcher(dp):
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("predict", predict_command))
    dp.add_handler(CommandHandler("nextmatch", nextmatch))
    dp.add_handler(MessageHandler(filters.TEXT, handle_text))
    dp.add_handler(CallbackQueryHandler(inline_handler))
# telegrambot/management/commands/runbot.py

from django.core.management.base import BaseCommand
from telegrambot.views import application

class Command(BaseCommand):
    help = "Run the Telegram bot application"

    def handle(self, *args, **kwargs):
        # This will run the application event loop (asyncio)
        application.run_polling()
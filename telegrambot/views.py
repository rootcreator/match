import json
import os
import joblib
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from telegram import Update, Bot
from telegram.ext import Dispatcher

from .dispatcher import setup_dispatcher

TOKEN = "8084516709:AAFZiSWDBm_raXMqUEpDqF4_GrOgqvgxe64"
bot = Bot(token=TOKEN)

# Create dispatcher once globally
dispatcher = Dispatcher(bot, None, use_context=True)
setup_dispatcher(dispatcher)

@csrf_exempt
def webhook(request):
    if request.method == "POST":
        data = json.loads(request.body)
        update = Update.de_json(data, bot)
        dispatcher.process_update(update)
        return JsonResponse({"status": "ok"})
    return JsonResponse({"status": "only POST allowed"})
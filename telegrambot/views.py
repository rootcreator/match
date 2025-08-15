# telegrambot/views.py

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder

from .dispatcher import setup_application

TOKEN = "8084516709:AAFZiSWDBm_raXMqUEpDqF4_GrOgqvgxe64"

# Create your Application once globally
application = ApplicationBuilder().token(TOKEN).build()
setup_application(application)

@csrf_exempt
def webhook(request):
    if request.method == "POST":
        data = json.loads(request.body)
        update = Update.de_json(data)
        
        # Process update asynchronously by passing it to application
        application.update_queue.put(update)
        
        return JsonResponse({"status": "ok"})
    else:
        return JsonResponse({"status": "only POST allowed"})
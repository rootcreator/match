# telegram_bot/views.py (your webhook view)
"""
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from telegram import Update, Bot
from telegram.ext import Dispatcher

from tenants.models import Tenant, User, OnboardingState, set_current_tenant
from .dispatcher import setup_dispatcher

TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
bot = Bot(token=TOKEN)
dispatcher = Dispatcher(bot, None, use_context=True)
setup_dispatcher(dispatcher)


@csrf_exempt
def webhook(request):
    if request.method != "POST":
        return JsonResponse({"status": "only POST allowed"}, status=405)

    data = json.loads(request.body)
    update = Update.de_json(data, bot)

    telegram_user_id = None
    if update.message:
        telegram_user_id = str(update.message.from_user.id)
    elif update.callback_query:
        telegram_user_id = str(update.callback_query.from_user.id)
    # Add other update types if needed

    tenant = None
    user = None

    if telegram_user_id:
        # Try tenant owner lookup
        tenant = Tenant.objects.filter(telegram_owner_user_id=telegram_user_id).first()

        if not tenant:
            # Try user lookup
            user = User.objects.filter(telegram_user_id=telegram_user_id).first()
            if user:
                tenant = user.tenant

        if tenant:
            set_current_tenant(tenant)

        else:
            # No tenant/user found → onboarding prompt
            onboarding, created = OnboardingState.objects.get_or_create(
                telegram_user_id=telegram_user_id,
                defaults={"state": "awaiting_email"}
            )
            if created or onboarding.state != "completed":
                bot.send_message(
                    chat_id=telegram_user_id,
                    text="Welcome! Please send me your email address to get started."
                )
                # Skip further processing; wait for user input on onboarding
                return JsonResponse({"status": "onboarding started"})

    else:
        # No Telegram user ID found in update
        pass

    # Process update (commands and messages)
    dispatcher.process_update(update)
    return JsonResponse({"status": "ok"})
"""
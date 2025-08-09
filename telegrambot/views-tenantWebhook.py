import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from telegram import Update, Bot
from telegram.ext import Dispatcher

from tenants.models import Tenant, User, set_current_tenant
from .dispatcher import setup_dispatcher

TOKEN = "8084516709:AAFZiSWDBm_raXMqUEpDqF4_GrOgqvgxe64"
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
        # 1. Try to find tenant by tenant owner Telegram user ID
        tenant = Tenant.objects.filter(telegram_owner_user_id=telegram_user_id).first()

        if tenant is None:
            # 2. Try to find user and tenant by telegram_user_id
            user = User.objects.filter(telegram_user_id=telegram_user_id).first()
            if user:
                tenant = user.tenant

        if tenant:
            set_current_tenant(tenant)

        else:
            # Tenant/user unknown — handle onboarding here
            # For example, reply via bot or set a flag to ask for tenant code
            # You can also skip set_current_tenant to block processing
            pass

    else:
        # No user ID found in update — proceed with caution or reject
        pass

    # Now process the update as usual
    dispatcher.process_update(update)
    return JsonResponse({"status": "ok"})
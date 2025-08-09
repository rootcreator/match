# telegram_bot/handlers/onboarding.py
"""
from telegram import Update
from telegram.ext import CallbackContext
from tenants.models import OnboardingState, Tenant, User
from tenants.models import set_current_tenant
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

def onboarding_handler(update: Update, context: CallbackContext):
    telegram_user_id = str(update.message.from_user.id)
    text = update.message.text.strip()

    try:
        onboarding = OnboardingState.objects.get(telegram_user_id=telegram_user_id)
    except OnboardingState.DoesNotExist:
        # Not in onboarding state — let other handlers handle this
        return

    if onboarding.state == "awaiting_email":
        # Validate email format
        try:
            validate_email(text)
        except ValidationError:
            update.message.reply_text("That doesn't look like a valid email. Please try again.")
            return

        onboarding.temp_email = text
        onboarding.state = "awaiting_phone"
        onboarding.save()
        update.message.reply_text("Thanks! Now, please send me your phone number.")

    elif onboarding.state == "awaiting_phone":
        # Basic phone validation (customize as needed)
        if len(text) < 7 or not text.replace("+", "").isdigit():
            update.message.reply_text("Please send a valid phone number including country code.")
            return

        onboarding.temp_phone = text

        email_domain = onboarding.temp_email.split("@")[-1].lower()
        tenant = Tenant.objects.filter(domain=email_domain).first()

        if not tenant:
            tenant = Tenant.objects.create(
                name=email_domain,
                slug=email_domain.replace(".", "-"),
                domain=email_domain,
                telegram_owner_user_id=telegram_user_id  # Owner is this telegram user
            )

        # Create or update user with telegram_user_id (explicitly passed)
        user, created = User.objects.update_or_create(
            telegram_user_id=telegram_user_id,
            defaults={
                "username": onboarding.temp_email.split("@")[0],
                "email": onboarding.temp_email,
                "phone_number": onboarding.temp_phone,
                "tenant": tenant,
            }
        )

        # Set tenant context for this session
        set_current_tenant(tenant)

        onboarding.state = "completed"
        onboarding.save()

        update.message.reply_text(
            f"Thanks for registering! Your Telegram ID ({telegram_user_id}) is now linked. "
            f"You are associated with tenant '{tenant.name}'. You can now use the bot."
        )

    elif onboarding.state == "completed":
        # Already onboarded; let other handlers take over
        return
"""
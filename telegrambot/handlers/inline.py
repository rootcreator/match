from telegram import Update
from telegram.ext import CallbackContext
from matches.models import Match
from matches.logic.feature_training import calculate_form

def inline_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    data = query.data
    action, match_id = data.split(":")
    match = Match.objects.get(id=match_id)

    if action == "form":
        form_home = calculate_form(match.home_team)
        form_away = calculate_form(match.away_team)
        query.edit_message_text(
            f"📊 Form:\n\n"
            f"{match.home_team}: {form_home}\n"
            f"{match.away_team}: {form_away}"
        )
    elif action == "h2h":
        query.edit_message_text("⚔️ Head-to-head data coming soon.")
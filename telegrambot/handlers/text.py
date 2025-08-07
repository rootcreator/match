from telegram import Update
from telegram.ext import CallbackContext
from .predict import predict_command
from .utils import parse_teams_from_text

def handle_text(update: Update, context: CallbackContext):
    text = update.message.text
    team_a, team_b = parse_teams_from_text(text)
    if team_a and team_b:
        context.args = [team_a, team_b]
        return predict_command(update, context)
    else:
        update.message.reply_text("Try: /predict Chelsea Arsenal or ask: Who will win between Barca and Madrid?")
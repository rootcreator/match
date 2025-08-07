from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from matches.models import Match
from logic.predict import extract_features
from django.utils import timezone
import os, joblib

MODEL_PATH = os.path.join(os.path.dirname(__file__), '../../model.pkl')
model = joblib.load(MODEL_PATH)

def predict_command(update, context):
    args = context.args
    if len(args) < 2:
        update.message.reply_text("Usage: /predict <Team A> <Team B>")
        return

    team_a = " ".join(args[:-1])
    team_b = args[-1]

    match = Match.objects.filter(
        home_team__icontains=team_a,
        away_team__icontains=team_b,
        date__gte=timezone.now()
    ).order_by('date').first()

    if not match:
        update.message.reply_text("Match not found.")
        return

    try:
        features = extract_features(match)
        prediction = model.predict([features])[0]
        odds = [0.5, 2.1, 3.3]  # Replace with actual `calculate_odds` logic

        msg = (
            f"🔮 *Prediction* for {match.home_team} vs {match.away_team}:\n"
            f"→ *Outcome*: {prediction.upper()}\n"
            f"→ *Odds*: {odds}"
        )

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📊 Form", callback_data=f"form:{match.id}")],
            [InlineKeyboardButton("⚔️ H2H", callback_data=f"h2h:{match.id}")]
        ])

        update.message.reply_text(msg, parse_mode="Markdown", reply_markup=keyboard)

    except Exception as e:
        update.message.reply_text(f"Error: {str(e)}")


def nextmatch(update, context):
    match = Match.objects.filter(date__gte=timezone.now()).order_by('date').first()
    if not match:
        update.message.reply_text("No upcoming matches found.")
        return

    try:
        features = extract_features(match)
        prediction = model.predict([features])[0]
        update.message.reply_text(
            f"Next Match: {match.home_team} vs {match.away_team}\n"
            f"→ Prediction: {prediction.upper()}"
        )
    except Exception as e:
        update.message.reply_text(f"Error: {str(e)}")
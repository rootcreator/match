import logging
from asgiref.sync import sync_to_async
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from django.db.models import Q
from matches.models import Prediction

logger = logging.getLogger(__name__)

@sync_to_async
def get_prediction(team_a: str, team_b: str):
    """Query the Prediction model for saved results (handles both orders)."""
    return (
        Prediction.objects
        .filter(
            # Either home vs away...
            (
                Q(fixture__home_team__name__icontains=team_a) &
                Q(fixture__away_team__name__icontains=team_b)
            )
            # ...or away vs home
            | (
                Q(fixture__home_team__name__icontains=team_b) &
                Q(fixture__away_team__name__icontains=team_a)
            )
        )
        .select_related(
            "fixture__home_team",
            "fixture__away_team"
        )
        .first()
    )

async def predict_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /predict command by fetching from Prediction model."""
    try:
        text = " ".join(context.args)

        if " vs " not in text.lower():
            await update.message.reply_text(
                "Usage: /predict <Team A> vs <Team B>\n"
                "Example: /predict Arsenal vs Manchester United"
            )
            return

        team_a, team_b = [t.strip() for t in text.split(" vs ", 1)]

        pred = await get_prediction(team_a, team_b)

        if not pred:
            await update.message.reply_text("❌ Prediction not found in database.")
            return

        msg = (
            f"🔮 *Prediction* for {pred.fixture.home_team} vs {pred.fixture.away_team}:\n"
            f"→ *Outcome*: {pred.result_pred.upper()}\n"
            f"→ *Confidence*: {pred.confidence:.1f}%\n"
            f"→ *Fair Odds*: Home {pred.fair_odds_home}, Draw {pred.fair_odds_draw}, Away {pred.fair_odds_away}"
        )

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📊 Form", callback_data=f"form:{pred.fixture.id}")],
            [InlineKeyboardButton("⚔️ H2H", callback_data=f"h2h:{pred.fixture.id}")]
        ])

        await update.message.reply_text(
            msg,
            parse_mode="Markdown",
            reply_markup=keyboard
        )

    except Exception as e:
        logger.error(f"Error in predict_command: {e}", exc_info=True)
        await update.message.reply_text("⚠️ An error occurred while fetching the prediction.")
from django.core.management.base import BaseCommand
from matches.models import Bet

class Command(BaseCommand):
    help = 'Settle bets after results are known'

    def handle(self, *args, **kwargs):
        bets = Bet.objects.filter(is_settled=False, match__result__isnull=False)

        for bet in bets:
            correct = bet.predicted_result == bet.match.result
            payout = bet.amount * bet.odds if correct else 0.0

            bet.win = correct
            bet.payout = payout
            bet.is_settled = True
            bet.save()

            outcome = "✅ WON" if correct else "❌ LOST"
            print(f"{outcome}: {bet.user} - {bet.match} - {bet.predicted_result} @ {bet.odds}")
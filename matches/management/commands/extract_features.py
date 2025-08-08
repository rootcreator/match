from django.core.management.base import BaseCommand
from matches.models import Match
from matches.logic.feature_training import calculate_form, calculate_strength, count_injuries

def extract_features(match):
    home = match.home_team
    away = match.away_team

    return {
        "home_form": calculate_form(home),
        "away_form": calculate_form(away),
        "home_strength": calculate_strength(home),
        "away_strength": calculate_strength(away),
        "home_injuries": count_injuries(home),
        "away_injuries": count_injuries(away),
    }

class Command(BaseCommand):
    help = "Extracts features for all matches and prints them."

    def add_arguments(self, parser):
        parser.add_argument(
            '--upcoming',
            action='store_true',
            help='Only extract features for upcoming matches.'
        )

    def handle(self, *args, **options):
        if options['upcoming']:
            matches = Match.objects.filter(result__isnull=True)
        else:
            matches = Match.objects.all()

        if not matches.exists():
            self.stdout.write(self.style.WARNING("No matches found."))
            return

        for match in matches:
            features = extract_features(match)
            self.stdout.write(
                f"Match {match.id} ({match.home_team} vs {match.away_team}): {features}"
            )

        self.stdout.write(self.style.SUCCESS("✅ Feature extraction complete."))

from django.core.management.base import BaseCommand
from matches.models import Match, Team
from matches.api_client import get_past_fixtures
from datetime import datetime


class Command(BaseCommand):
    help = "Sync past finished matches into Match model"

    def handle(self, *args, **kwargs):
        league_id = 39  # EPL
        season = 2023
        past_fixtures = get_past_fixtures(league_id=league_id, season=season, count=50)

        for item in past_fixtures['response']:
            fixture = item['fixture']
            teams = item['teams']
            score = item['score']

            fixture_id = fixture['id']
            date = fixture['date']
            status = fixture['status']['short']

            home_team_api_id = teams['home']['id']
            away_team_api_id = teams['away']['id']

            try:
                home_team = Team.objects.get(api_id=home_team_api_id)
                away_team = Team.objects.get(api_id=away_team_api_id)
            except Team.DoesNotExist:
                self.stderr.write(f"🚫 Teams not found for fixture {fixture_id}")
                continue

            home_goals = score['fulltime']['home']
            away_goals = score['fulltime']['away']

            if home_goals is None or away_goals is None:
                continue

            # Determine match result from perspective of home team
            if home_goals > away_goals:
                result = 'win'
            elif home_goals < away_goals:
                result = 'loss'
            else:
                result = 'draw'

            match, created = Match.objects.update_or_create(
                fixture_id=fixture_id,
                defaults={
                    'home_team': home_team,
                    'away_team': away_team,
                    'date': date,
                    'home_score': home_goals,
                    'away_score': away_goals,
                    'result': result
                }
            )

            if created:
                self.stdout.write(f"✅ Added match {home_team} vs {away_team}")
            else:
                self.stdout.write(f"🔁 Updated match {home_team} vs {away_team}")
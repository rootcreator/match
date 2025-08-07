from django.core.management.base import BaseCommand
from matches.models import Fixture, Team
from matches.api_client import get_fixtures
from django.utils.dateparse import parse_datetime


class Command(BaseCommand):
    help = "Sync upcoming fixtures from API"

    def handle(self, *args, **kwargs):
        fixtures_data = get_fixtures(next_n=20)

        for item in fixtures_data['response']:
            fixture_info = item['fixture']
            home_info = item['teams']['home']
            away_info = item['teams']['away']

            # Ensure home team exists
            home_team, _ = Team.objects.get_or_create(
                api_id=home_info['id'],
                defaults={
                    'name': home_info['name'],
                    'league': 'Unknown'  # You can sync league data separately
                }
            )

            # Ensure away team exists
            away_team, _ = Team.objects.get_or_create(
                api_id=away_info['id'],
                defaults={
                    'name': away_info['name'],
                    'league': 'Unknown'
                }
            )

            # Create or update Fixture
            fixture, created = Fixture.objects.update_or_create(
                id=fixture_info['id'],
                defaults={
                    'date': parse_datetime(fixture_info['date']),
                    'status': fixture_info['status']['long'],
                    'home_team': home_team,
                    'away_team': away_team
                }
            )

            action = "Created" if created else "Updated"
            self.stdout.write(f"{action} fixture: {home_team.name} vs {away_team.name}")
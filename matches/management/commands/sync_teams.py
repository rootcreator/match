from django.core.management.base import BaseCommand
from matches.api_client import get_teams
from matches.models import Team

class Command(BaseCommand):
    help = 'Sync teams from API-Football'

    def handle(self, *args, **kwargs):
        data = get_teams()
        for entry in data['response']:
            team_info = entry['team']
            name = team_info['name']
            api_id = team_info['id']
            league = "Premier League"  # or manually map by league_id

            team, created = Team.objects.get_or_create(
                api_id=api_id,
                defaults={'name': name, 'league': league}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Added team: {name}'))
            else:
                self.stdout.write(f'Exists: {name}')
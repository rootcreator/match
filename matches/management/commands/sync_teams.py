from django.core.management.base import BaseCommand
from matches.api_client import get_teams, get_leagues
from matches.models import Team
import re

def slugify_league_name(name, country):
    """
    Convert league name + country to CLI flag format:
    'Serie A', 'Italy' -> 'serie-a-italy'
    """
    full_name = f"{name} {country}"
    return re.sub(r'[^a-z0-9]+', '-', full_name.lower()).strip('-')

class Command(BaseCommand):
    help = 'Sync teams from API-Football for major leagues only (auto league mapping)'

    # Define which leagues we care about
    MAJOR_LEAGUES = {
        "Premier League": "England",
        "Bundesliga": "Germany",
        "La Liga": "Spain",
        "Serie A": "Italy",
        "Ligue 1": "France",
        "Eredivisie": "Netherlands",
        "Primeira Liga": "Portugal",
        "Major League Soccer": "USA",
        "Brasileirão Serie A": "Brazil",
    }

    def add_arguments(self, parser):
        parser.add_argument('--season', type=int, required=True, help='Season year')

        # Fetch leagues dynamically
        leagues_data = get_leagues()
        self.league_map = {}

        for entry in leagues_data['response']:
            league_name = entry['league']['name']
            league_id = entry['league']['id']
            country = entry['country']['name']

            # Only include if in our major leagues filter
            if league_name in self.MAJOR_LEAGUES and self.MAJOR_LEAGUES[league_name] == country:
                slug = slugify_league_name(league_name, country)
                self.league_map[slug] = {
                    'id': league_id,
                    'name': league_name,
                    'country': country
                }

                parser.add_argument(
                    f'--{slug}',
                    action='store_true',
                    help=f"Sync teams for {league_name} ({country})"
                )

    def handle(self, *args, **kwargs):
        season = kwargs['season']

        # Detect which league flag was passed
        league_choice = None
        for slug, details in self.league_map.items():
            if kwargs[slug.replace('-', '_')]:  # argparse converts - to _
                league_choice = details
                break

        if not league_choice:
            self.stdout.write(self.style.ERROR(
                "Please specify a major league flag. Example: --premier-league-england --season 2024"
            ))
            return

        league_id = league_choice['id']
        league_name = league_choice['name']
        country_name = league_choice['country']

        self.stdout.write(self.style.NOTICE(
            f"Syncing teams for {league_name} ({country_name}) - Season {season}"
        ))

        # Fetch teams from API-Football
        data = get_teams(league_id, season)
        for entry in data['response']:
            team_info = entry['team']
            name = team_info['name']
            api_id = team_info['id']

            team, created = Team.objects.get_or_create(
                api_id=api_id,
                defaults={'name': name, 'league': league_name}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Added team: {name}'))
            else:
                self.stdout.write(f'Exists: {name}')

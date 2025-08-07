from django.core.management.base import BaseCommand
from matches.models import Player, Team
from matches.api_client import get_players_by_team


class Command(BaseCommand):
    help = "Sync players for all teams"

    def handle(self, *args, **kwargs):
        for team in Team.objects.all():
            self.stdout.write(f"\n🔄 Syncing players for team: {team.name} (ID: {team.api_id})")
            try:
                data = get_players_by_team(team.api_id)
                players = data.get('response', [])

                for player_entry in players:
                    player_info = player_entry.get('player', {})
                    injured = player_info.get('injured', False)
                    position = player_info.get('position', 'Unknown')

                    # Create or update player
                    Player.objects.update_or_create(
                        name=player_info['name'],
                        team=team,
                        defaults={
                            'position': position,
                            'injured': injured,
                        }
                    )

                self.stdout.write(f"✅ {len(players)} players synced for {team.name}")

            except Exception as e:
                self.stderr.write(f"❌ Error syncing team {team.name}: {e}")
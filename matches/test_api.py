from matches.api_client import get_teams

teams_data = get_teams()
for team in teams_data['response']:
    print(team['team']['name'])
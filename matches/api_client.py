import requests
import datetime


API_KEY = '1ecad14232mshea32a62c1e4dc2ap181062jsn38bf6995676a'  # Replace this
BASE_URL = 'https://api-football-v1.p.rapidapi.com/v3'

HEADERS = {
    'X-RapidAPI-Key': API_KEY,
    'X-RapidAPI-Host': 'api-football-v1.p.rapidapi.com'
}

def get_leagues():
    url = f'{BASE_URL}/leagues'
    response = requests.get(url, headers=HEADERS)
    return response.json()

def get_teams(league_id=39, season=2025):  # EPL example
    url = f'{BASE_URL}/teams'
    params = {'league': league_id, 'season': season}
    response = requests.get(url, headers=HEADERS, params=params)
    return response.json()



def get_fixtures(next_n=10):
    """
    Fetch the next N fixtures using API-Football v3.
    """
    url = f"{BASE_URL}/fixtures"
    params = {
        "next": next_n
    }

    response = requests.get(url, headers=HEADERS, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API Error {response.status_code}: {response.text}")
        
        
def get_players_by_team(team_id, season=2023):
    url = f"{BASE_URL}/players"
    params = {
        'team': team_id,
        'season': season
    }
    response = requests.get(url, headers=HEADERS, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API Error {response.status_code}: {response.text}")
        
        
def get_past_fixtures(league_id=39, season=2023, count=50):
    url = f"{BASE_URL}/fixtures"
    params = {
        'league': league_id,
        'season': season,
        'status': 'FT',  # Finished matches
        'last': count
    }

    response = requests.get(url, headers=HEADERS, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API Error {response.status_code}: {response.text}")
        
        

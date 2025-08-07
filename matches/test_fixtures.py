from matches.api_client import get_fixtures

fixtures = get_fixtures()
print(f"Total fixtures: {len(fixtures['response'])}")
for f in fixtures['response'][:5]:
    print(f['fixture']['id'], f['teams']['home']['name'], 'vs', f['teams']['away']['name'])
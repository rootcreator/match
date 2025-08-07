import re

def parse_teams_from_text(text: str):
    match = re.search(r"between ([\w\s]+) and ([\w\s]+)", text, re.IGNORECASE)
    if match:
        team_a = match.group(1).strip()
        team_b = match.group(2).strip()
        return team_a, team_b
    return None, None
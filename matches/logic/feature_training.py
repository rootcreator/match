from matches.models import Match, Player
from django.db.models import Q

def get_recent_matches(team, limit=5):
    return Match.objects.filter(
        Q(home_team=team) | Q(away_team=team),
        home_score__isnull=False,
        away_score__isnull=False
    ).order_by('-date')[:limit]

def calculate_form(team):
    matches = get_recent_matches(team, limit=5)
    score = 0
    for m in matches:
        if m.home_team == team:
            if m.home_score > m.away_score:
                score += 3
            elif m.home_score == m.away_score:
                score += 1
        elif m.away_team == team:
            if m.away_score > m.home_score:
                score += 3
            elif m.away_score == m.home_score:
                score += 1
    return score / 15  # Normalize to 0–1

def calculate_strength(team):
    matches = get_recent_matches(team, limit=10)
    scored = conceded = 0
    for m in matches:
        if m.home_team == team:
            scored += m.home_score
            conceded += m.away_score
        else:
            scored += m.away_score
            conceded += m.home_score
    return (scored - conceded) / 10 if matches else 0

def count_injuries(team):
    return Player.objects.filter(team=team, injured=True).count()
from matches.logic.feature_engineering import calculate_form, calculate_strength, count_injuries

def extract_features(match):
    home = match.home_team
    away = match.away_team

    return {
        "home_form": calculate_form(home),
        "away_form": calculate_form(away),
        "home_strength": calculate_strength(home),
        "away_strength": calculate_strength(away),
        "home_injuries": count_injuries(home),
        "away_injuries": count_injuries(away),
    }
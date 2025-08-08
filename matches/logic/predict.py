from matches.logic.feature_training import calculate_form, calculate_strength, count_injuries

def extract_features(obj):
    """
    Extracts features from either a Match (historical) or Fixture (upcoming).
    """
    # Works for both Match and Fixture as long as they have home_team and away_team
    home = getattr(obj, 'home_team', None)
    away = getattr(obj, 'away_team', None)

    if not home or not away:
        raise ValueError("Object must have home_team and away_team attributes.")

    return {
        "home_form": calculate_form(home),
        "away_form": calculate_form(away),
        "home_strength": calculate_strength(home),
        "away_strength": calculate_strength(away),
        "home_injuries": count_injuries(home),
        "away_injuries": count_injuries(away),
    }

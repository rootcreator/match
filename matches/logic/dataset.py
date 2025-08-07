# matches/logic/dataset.py

from matches.models import Match
from matches.logic.predict import extract_features

def build_dataset():
    data = []
    labels = []

    matches = Match.objects.filter(
        home_score__isnull=False,
        away_score__isnull=False
    )

    for match in matches:
        features = extract_features(match)
        result = match.result  # Expected: 'win', 'draw', or 'loss'
        if result:
            data.append(list(features.values()))
            labels.append(result)

    return data, labels
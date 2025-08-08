from matches.models import Match, Prediction, Fixture
from matches.logic.predict import extract_features
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

label_map = {0: 'win', 1: 'draw', 2: 'loss'}
reverse_map = {'win': 0, 'draw': 1, 'loss': 2}

def train_and_predict():
    # TRAIN FROM PAST MATCHES
    past_matches = Match.objects.exclude(result__isnull=True)
    X, y = [], []

    for match in past_matches:
        features = extract_features(match)
        X.append([
            features['home_form'],
            features['away_form'],
            features['home_strength'],
            features['away_strength'],
            features['home_injuries'],
            features['away_injuries']
        ])
        y.append(reverse_map[match.result])

    if not X:
        return {"status": "fail", "reason": "No historical data"}

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    accuracy = accuracy_score(y_test, model.predict(X_test))

    # PREDICT FOR UPCOMING FIXTURES
    upcoming_fixtures = Fixture.objects.filter(status__icontains="Not Started")
    matches_predicted = 0

    for fixture in upcoming_fixtures:
        # Assuming extract_features can handle Fixture objects
        features = extract_features(fixture)
        X_fixture = [[
            features['home_form'],
            features['away_form'],
            features['home_strength'],
            features['away_strength'],
            features['home_injuries'],
            features['away_injuries']
        ]]

        pred = model.predict(X_fixture)[0]
        probs = model.predict_proba(X_fixture)[0]

        Prediction.objects.update_or_create(
            fixture=fixture,
            defaults={
                'result_pred': label_map[pred],
                'confidence': float(max(probs)),
                'goal_diff': features['home_strength'] - features['away_strength'],
                'fair_odds_home': round(1 / probs[0], 2),
                'fair_odds_draw': round(1 / probs[1], 2),
                'fair_odds_away': round(1 / probs[2], 2),
            }
        )
        matches_predicted += 1

    return {
        "status": "success",
        "accuracy": round(accuracy, 4),
        "matches_predicted": matches_predicted
    }

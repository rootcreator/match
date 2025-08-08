import os
import joblib
from django.core.management.base import BaseCommand
from matches.models import Match, Prediction
from matches.logic.predict import extract_features
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

MODEL_PATH = os.path.join('matches', 'models', 'ml_model.pkl')


class Command(BaseCommand):
    help = 'Train or load model and predict upcoming matches'

    def add_arguments(self, parser):
        parser.add_argument(
            '--model-version',
            type=str,
            default='v1',
            help='Model version to tag predictions with'
    )


    def handle(self, *args, **kwargs):
        model_version = kwargs.get('model_version', 'v1')
        model = None

        if os.path.exists(MODEL_PATH):
            print("📦 Loading saved model...")
            model = joblib.load(MODEL_PATH)
        else:
            print("🔨 Training new model (no saved model found)...")
            model = self.train_and_save_model()

        if model:
            self.predict_upcoming(model, model_version)
        else:
            print("❌ Model unavailable. Aborting.")

    def train_and_save_model(self):
        past_matches = Match.objects.exclude(result__isnull=True)
        X, y = [], []

        for match in past_matches:
            try:
                f = extract_features(match)
                X.append([
                    f["home_form"],
                    f["away_form"],
                    f["home_strength"],
                    f["away_strength"],
                    f["home_injuries"],
                    f["away_injuries"],
                ])
                y.append({'win': 0, 'draw': 1, 'loss': 2}[match.result])
            except Exception as e:
                print(f"⚠️ Skipping match {match.id}: {e}")
                continue

        if not X:
            print("⚠️ No valid data to train.")
            return None

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)

        acc = accuracy_score(y_test, model.predict(X_test))
        print(f"🎯 Model trained. Accuracy: {acc:.2%}")

        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        joblib.dump(model, MODEL_PATH)
        print(f"💾 Model saved to {MODEL_PATH}")

        return model

    def predict_upcoming(self, model, model_version):
        label_map = {0: 'win', 1: 'draw', 2: 'loss'}
        upcoming = Match.objects.filter(result__isnull=True)

        print("🔍 Predicting upcoming matches...")

        for match in upcoming:
            try:
                f = extract_features(match)
                X_pred = [[
                    f["home_form"],
                    f["away_form"],
                    f["home_strength"],
                    f["away_strength"],
                    f["home_injuries"],
                    f["away_injuries"],
                ]]

                pred = model.predict(X_pred)[0]
                probs = model.predict_proba(X_pred)[0]

                Prediction.objects.update_or_create(
                    match=match,
                    defaults={
                        'result_pred': label_map[pred],
                        'confidence': float(max(probs)),
                        'goal_diff': int(round(probs[0] * 2 - probs[2] * 2)),
                        'fair_odds_home': round(1 / probs[0], 2),
                        'fair_odds_draw': round(1 / probs[1], 2),
                        'fair_odds_away': round(1 / probs[2], 2),
                        'model_version': model_version,
                    }
                )
                print(f"✅ Prediction saved: {match} → {label_map[pred]} (conf: {max(probs):.2f})")

            except Exception as e:
                print(f"⚠️ Match {match.id} failed prediction: {e}")

        print("🏁 Prediction phase completed.")

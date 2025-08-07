from rest_framework import serializers
from matches.models import Prediction, Match

class MatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = ['id', 'home_team', 'away_team', 'match_date']

class PredictionSerializer(serializers.ModelSerializer):
    match = MatchSerializer(read_only=True)

    class Meta:
        model = Prediction
        fields = [
            'id', 'match', 'result_pred', 'confidence',
            'goal_diff', 'fair_odds_home', 'fair_odds_draw', 'fair_odds_away',
        ]
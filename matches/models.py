from django.db import models
from django.contrib.auth.models import User

class Team(models.Model):
    name = models.CharField(max_length=100)
    league = models.CharField(max_length=100)
    api_id = models.IntegerField(unique=True)

    def __str__(self):
        return self.name

class Fixture(models.Model):
    id = models.IntegerField(primary_key=True)
    date = models.DateTimeField()
    status = models.CharField(max_length=50)
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='home_fixtures')
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='away_fixtures')

    def __str__(self):
        return f"{self.home_team} vs {self.away_team}"

class Player(models.Model):
    name = models.CharField(max_length=100)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    position = models.CharField(max_length=50)
    injured = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.team.name})"

class Match(models.Model):
    fixture_id = models.IntegerField(unique=True)  # new field
    home_team = models.ForeignKey(Team, related_name='home_matches', on_delete=models.CASCADE)
    away_team = models.ForeignKey(Team, related_name='away_matches', on_delete=models.CASCADE)
    date = models.DateTimeField()
    home_score = models.IntegerField(null=True, blank=True)
    away_score = models.IntegerField(null=True, blank=True)
    result = models.CharField(max_length=10, choices=[('win', 'Win'), ('draw', 'Draw'), ('loss', 'Loss')], null=True, blank=True)

    def __str__(self):
        return f"{self.home_team.name} vs {self.away_team.name}"

class Prediction(models.Model):
    match = models.OneToOneField(Match, on_delete=models.CASCADE)
    result_pred = models.CharField(max_length=10, choices=[('win', 'Win'), ('draw', 'Draw'), ('loss', 'Loss')])
    confidence = models.FloatField()
    goal_diff = models.IntegerField()
    fair_odds_home = models.FloatField()
    fair_odds_draw = models.FloatField()
    fair_odds_away = models.FloatField()
    model_version = models.CharField(max_length=20, default='v1')  # 🔁 Add this

    def __str__(self):
        return f"Prediction for {self.match}"

class UserPrediction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    predicted_result = models.CharField(max_length=10)  # win/draw/loss
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'match')

class Bet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    predicted_result = models.CharField(max_length=10)  # win/draw/loss
    amount = models.FloatField()
    odds = models.FloatField()
    is_settled = models.BooleanField(default=False)
    win = models.BooleanField(null=True, blank=True)  # null until settled
    payout = models.FloatField(default=0.0)
    placed_at = models.DateTimeField(auto_now_add=True)
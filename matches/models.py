import csv
import json
from django.db import models
from django.contrib.auth.models import User
from django.utils.dateparse import parse_datetime

class Team(models.Model):
    name = models.CharField(max_length=100)
    league = models.CharField(max_length=100)
    api_id = models.IntegerField(unique=True, null=True, blank=True)

    def __str__(self):
        return self.name

    @classmethod
    def import_from_csv(cls, file_path):
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                cls.objects.update_or_create(
                    api_id=row['api_id'],
                    defaults={
                        'name': row['name'],
                        'league': row['league'],
                    }
                )

    @classmethod
    def import_from_json(cls, file_path):
        with open(file_path, encoding='utf-8') as jsonfile:
            data = json.load(jsonfile)
            for item in data:
                cls.objects.update_or_create(
                    api_id=item['api_id'],
                    defaults={
                        'name': item['name'],
                        'league': item['league'],
                    }
                )

class Fixture(models.Model):
    id = models.IntegerField(primary_key=True)
    date = models.DateTimeField()
    status = models.CharField(max_length=50)
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='home_fixtures')
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='away_fixtures')

    def __str__(self):
        return f"{self.home_team} vs {self.away_team}"

    @classmethod
    def import_from_csv(cls, file_path):
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                home_team = Team.objects.filter(api_id=row['home_team_api_id']).first()
                away_team = Team.objects.filter(api_id=row['away_team_api_id']).first()
                if not home_team or not away_team:
                    continue
                cls.objects.update_or_create(
                    id=int(row['id']),
                    defaults={
                        'date': parse_datetime(row['date']),
                        'status': row['status'],
                        'home_team': home_team,
                        'away_team': away_team,
                    }
                )

    @classmethod
    def import_from_json(cls, file_path):
        with open(file_path, encoding='utf-8') as jsonfile:
            data = json.load(jsonfile)
            for item in data:
                home_team = Team.objects.filter(api_id=item['home_team_api_id']).first()
                away_team = Team.objects.filter(api_id=item['away_team_api_id']).first()
                if not home_team or not away_team:
                    continue
                cls.objects.update_or_create(
                    id=int(item['id']),
                    defaults={
                        'date': parse_datetime(item['date']),
                        'status': item['status'],
                        'home_team': home_team,
                        'away_team': away_team,
                    }
                )

class Player(models.Model):
    name = models.CharField(max_length=100)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    position = models.CharField(max_length=50)
    injured = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.team.name})"

    @classmethod
    def import_from_csv(cls, file_path):
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                team = Team.objects.filter(api_id=row['team_api_id']).first()
                if not team:
                    continue
                cls.objects.update_or_create(
                    name=row['name'],
                    team=team,
                    defaults={
                        'position': row['position'],
                        'injured': row['injured'].lower() in ['true', '1', 'yes'],
                    }
                )

    @classmethod
    def import_from_json(cls, file_path):
        with open(file_path, encoding='utf-8') as jsonfile:
            data = json.load(jsonfile)
            for item in data:
                team = Team.objects.filter(api_id=item['team_api_id']).first()
                if not team:
                    continue
                cls.objects.update_or_create(
                    name=item['name'],
                    team=team,
                    defaults={
                        'position': item['position'],
                        'injured': item['injured'],
                    }
                )

class Match(models.Model):
    fixture_id = models.IntegerField(unique=True)  # new field
    home_team = models.ForeignKey(Team, related_name='home_matches', on_delete=models.CASCADE)
    away_team = models.ForeignKey(Team, related_name='away_matches', on_delete=models.CASCADE)
    date = models.DateTimeField()
    home_score = models.IntegerField(null=True, blank=True)
    away_score = models.IntegerField(null=True, blank=True)
    result = models.CharField(
        max_length=10,
        choices=[('win', 'Win'), ('draw', 'Draw'), ('loss', 'Loss')],
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.home_team.name} vs {self.away_team.name}"

    @classmethod
    def import_from_csv(cls, file_path):
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Create or get teams by name
                home_team, _ = Team.objects.get_or_create(name=row['Home Team'].strip())
                away_team, _ = Team.objects.get_or_create(name=row['Away Team'].strip())

                cls.objects.update_or_create(
                    fixture_id=int(row['Fixture ID']),
                    defaults={
                        'home_team': home_team,
                        'away_team': away_team,
                        'date': parse_datetime(row['Date']),
                        'home_score': int(row['Home Score']) if 'Home Score' in row and row['Home Score'] else None,
                        'away_score': int(row['Away Score']) if 'Away Score' in row and row['Away Score'] else None,
                        'result': row['Result'].lower() if row['Result'] and row['Result'].lower() in ['win', 'draw', 'loss'] else None,
                    }
                )

    @classmethod
    def import_from_json(cls, file_path):
        with open(file_path, encoding='utf-8') as jsonfile:
            data = json.load(jsonfile)
            for item in data:
                # Create or get teams by name
                home_team, _ = Team.objects.get_or_create(name=item['Home Team'].strip())
                away_team, _ = Team.objects.get_or_create(name=item['Away Team'].strip())

                cls.objects.update_or_create(
                    fixture_id=int(item['Fixture ID']),
                    defaults={
                        'home_team': home_team,
                        'away_team': away_team,
                        'date': parse_datetime(item['Date']),
                        'home_score': int(item['Home Score']) if 'Home Score' in item and item['Home Score'] else None,
                        'away_score': int(item['Away Score']) if 'Away Score' in item and item['Away Score'] else None,
                        'result': item['Result'].lower() if item.get('Result') and item['Result'].lower() in ['win', 'draw', 'loss'] else None,
                    }
                )
class Prediction(models.Model):
    fixture = models.ForeignKey(Fixture, on_delete=models.CASCADE)
    result_pred = models.CharField(max_length=10, choices=[('win', 'Win'), ('draw', 'Draw'), ('loss', 'Loss')])
    confidence = models.FloatField()
    goal_diff = models.IntegerField()
    fair_odds_home = models.FloatField()
    fair_odds_draw = models.FloatField()
    fair_odds_away = models.FloatField()
    model_version = models.CharField(max_length=20, default='v1')  # 🔁 Add this

    def __str__(self):
        return f"Prediction for {self.fixture}"

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

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    predicted_result = models.CharField(max_length=10)  # win/draw/loss
    amount = models.FloatField()
    odds = models.FloatField()
    is_settled = models.BooleanField(default=False)
    win = models.BooleanField(null=True, blank=True)  # null until settled
    payout = models.FloatField(default=0.0)
    placed_at = models.DateTimeField(auto_now_add=True)
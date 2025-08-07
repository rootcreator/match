from django import forms
from .models import Match

RESULT_CHOICES = [
    ('win', 'Win'),
    ('draw', 'Draw'),
    ('loss', 'Loss'),
]

class UserPredictionForm(forms.Form):
    match = forms.ModelChoiceField(queryset=Match.objects.filter(result__isnull=True))
    predicted_result = forms.ChoiceField(choices=RESULT_CHOICES)

class BetForm(forms.Form):
    match = forms.ModelChoiceField(queryset=Match.objects.filter(result__isnull=True))
    predicted_result = forms.ChoiceField(choices=RESULT_CHOICES)
    amount = forms.FloatField(min_value=1)
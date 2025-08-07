from django.shortcuts import render
from matches.models import Prediction

def predictions_template_view(request):
    version = request.GET.get('version', 'v1')
    predictions = Prediction.objects.filter(model_version=version).select_related('match').order_by('-match__date')[:30]

    return render(request, 'predictions_list.html', {
        'predictions': predictions,
        'version': version
    })
    
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from .forms import UserPredictionForm, BetForm
from .models import UserPrediction, Bet, Prediction

@login_required
def make_prediction(request):
    if request.method == 'POST':
        form = UserPredictionForm(request.POST)
        if form.is_valid():
            match = form.cleaned_data['match']
            result = form.cleaned_data['predicted_result']
            UserPrediction.objects.update_or_create(
                user=request.user,
                match=match,
                defaults={'predicted_result': result}
            )
            return redirect('predictions_template')
    else:
        form = UserPredictionForm()
    return render(request, 'make_prediction.html', {'form': form})

@login_required
def place_bet(request):
    if request.method == 'POST':
        form = BetForm(request.POST)
        if form.is_valid():
            match = form.cleaned_data['match']
            result = form.cleaned_data['predicted_result']
            amount = form.cleaned_data['amount']

            # Get fair odds from prediction
            prediction = Prediction.objects.filter(match=match).first()
            if not prediction:
                return HttpResponse("No prediction available yet.")

            odds_map = {
                'win': prediction.fair_odds_home,
                'draw': prediction.fair_odds_draw,
                'loss': prediction.fair_odds_away,
            }

            Bet.objects.create(
                user=request.user,
                match=match,
                predicted_result=result,
                amount=amount,
                odds=odds_map[result]
            )
            return redirect('bet_summary')
    else:
        form = BetForm()
    return render(request, 'place_bet.html', {'form': form})
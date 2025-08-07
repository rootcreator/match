from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from matches.models import Prediction, Match
from django.db.models import Count, Avg
import numpy as np

@api_view(['GET'])
@permission_classes([AllowAny])
def prediction_overview(request):
    total = Prediction.objects.count()
    confidence_avg = Prediction.objects.aggregate(avg=Avg('confidence'))['avg'] or 0

    correct = 0
    evaluated = 0
    for p in Prediction.objects.select_related('match'):
        if p.match.result:
            evaluated += 1
            if p.match.result == p.result_pred:
                correct += 1

    accuracy = correct / evaluated if evaluated else None

    return Response({
        "total_predictions": total,
        "evaluated_predictions": evaluated,
        "accuracy": round(accuracy, 4) if accuracy is not None else None,
        "avg_confidence": round(confidence_avg, 2),
    })
    
@api_view(['GET'])
@permission_classes([AllowAny])
def prediction_confidence_distribution(request):
    bins = [0, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    bucket_counts = {f"{int(bins[i]*100)}-{int(bins[i+1]*100)}": 0 for i in range(len(bins)-1)}

    for p in Prediction.objects.all():
        for i in range(len(bins)-1):
            if bins[i] <= p.confidence < bins[i+1]:
                label = f"{int(bins[i]*100)}-{int(bins[i+1]*100)}"
                bucket_counts[label] += 1
                break

    return Response(bucket_counts)

@api_view(['GET'])
@permission_classes([AllowAny])
def latest_predictions(request):
    predictions = Prediction.objects.select_related('match').order_by('-match__date')[:20]
    return Response([
        {
            "match": str(p.match),
            "prediction": p.result_pred,
            "confidence": p.confidence,
            "odds": {
                "home": p.fair_odds_home,
                "draw": p.fair_odds_draw,
                "away": p.fair_odds_away
            },
            "actual": p.match.result
        } for p in predictions
    ])
    
@api_view(['GET'])
@permission_classes([AllowAny])
def compare_versions(request):
    version_a = request.GET.get('a', 'v1')
    version_b = request.GET.get('b', 'v2')

    matches = Match.objects.filter(result__isnull=False)

    correct_a = correct_b = total = 0

    for match in matches:
        try:
            pred_a = Prediction.objects.get(match=match, model_version=version_a)
            pred_b = Prediction.objects.get(match=match, model_version=version_b)
        except Prediction.DoesNotExist:
            continue

        total += 1
        if pred_a.result_pred == match.result:
            correct_a += 1
        if pred_b.result_pred == match.result:
            correct_b += 1

    return Response({
        "version_a": version_a,
        "version_b": version_b,
        "accuracy_a": round(correct_a / total, 3) if total else None,
        "accuracy_b": round(correct_b / total, 3) if total else None,
        "compared_matches": total
    })
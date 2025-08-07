from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from matches.models import Prediction, Match
from matches.serializers import PredictionSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from matches.logic.train_and_predict import train_and_predict


class PredictionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Prediction.objects.select_related('match')
    serializer_class = PredictionSerializer

    @action(detail=False, methods=['get'], url_path='upcoming')
    def upcoming(self, request):
        upcoming_matches = Match.objects.filter(result__isnull=True)
        predictions = Prediction.objects.filter(match__in=upcoming_matches).select_related('match')
        serializer = self.get_serializer(predictions, many=True)
        return Response(serializer.data)
        
        

@api_view(['POST'])
@permission_classes([IsAdminUser])
def retrain_predictions(request):
    result = train_and_predict()

    if result['status'] == "fail":
        return Response(result, status=status.HTTP_400_BAD_REQUEST)

    return Response(result, status=status.HTTP_200_OK)
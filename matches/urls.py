from django.urls import path, include
from rest_framework.routers import DefaultRouter
from matches.views import PredictionViewSet, retrain_predictions

router = DefaultRouter()
router.register(r'predictions', PredictionViewSet, basename='prediction')
router.register(r'retrain', retrain_predictions, basename='retrain prediction')

urlpatterns = [
    path('api/', include(router.urls)),
]


from matches.views_dashboard import prediction_overview, prediction_confidence_distribution

urlpatterns += [
    path('api/dashboard/overview/', prediction_overview, name='dashboard_overview'),
    path('api/dashboard/confidence/', prediction_confidence_distribution, name='dashboard_confidence'),
    path('api/predictions/latest/', latest_predictions),
    path('api/dashboard/compare_versions/', compare_versions),
]

from matches.views_ui import predictions_template_view

path('dashboard/predictions/', predictions_template_view),
from django.urls import path
from .views import prediction_view


urlpatterns = [
    path("get-prediction/", prediction_view, name="get_prediction"),
]
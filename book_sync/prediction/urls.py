from django.urls import path

from . import views
from .views import prediction_view, category_preference_view, save_age

urlpatterns = [
    path("get-prediction/", prediction_view, name="get_prediction"),
    path("", category_preference_view, name="category_preference"),
    path('save-age/', views.save_age, name='save_age'),
]
from django.urls import path
from .views import prediction_view, category_preference_view, genre_preference_view

urlpatterns = [
    path("get-prediction/", prediction_view, name="get_prediction"),
    path("", category_preference_view, name="category_preference"),
    path("genres/", genre_preference_view, name="genre_preference"),
]
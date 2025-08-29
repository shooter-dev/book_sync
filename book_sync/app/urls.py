from django.urls import path, include
from .  import views

urlpatterns = [
    path("home/", views.index, name="index"),
    path("collection/", views.collection, name="collection"),
    path("recommendation/", views.recommendation, name="recommendation"),
    path("prediction/", views.prediction, name="prediction"),
    path("predict-responce/", views.predict_responce, name="predict-responce"),
]
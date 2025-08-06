from django.urls import path
from .  import views

urlpatterns = [
    path("home/", views.index, name="index"),
    path("research/", views.research, name="research"),
    path("collection/", views.collection, name="collection"),
    path("recommendation/", views.recommendation, name="recommendation"),
]
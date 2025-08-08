from django.urls import path
from .  import views
from django.contrib import admin

urlpatterns = [
    path("search/", views.search, name="search"),path("search/", views.search, name="search"),
    path("home", views.collection, name="collection"),
]
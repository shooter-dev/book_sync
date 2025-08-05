from django.contrib import admin
from django.urls import path
from .  import views

urlpatterns = [
    path("",views.index,name="index"),
    path("research", views.research, name="research"),
    path("collection", views.collection, name="collection"),
]
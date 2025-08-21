from django.urls import path
from .  import views
from django.contrib import admin

urlpatterns = [
    path("search/", views.search, name="search"),
    path("home/", views.collection, name="collection"),
    path("serie/<uuid:serie_id>/", views.serie_detail, name="serie_detail"),
    path("volume/<uuid:volume_id>/", views.volume_detail, name="volume_detail"),
    path('add/<uuid:volume_id>/', views.add_collection, name='add_collection'),
    path('delete/<uuid:volume_id>/', views.delete_volume_collection, name='delete_volume_collection'),
    path('popup-search/', views.popup_search, name='popup_search')
]
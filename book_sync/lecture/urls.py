from django.urls import path
from .  import views
from django.contrib import admin

urlpatterns = [
    path("", views.lecture, name="lecture"),
    path("mark-as-read/<uuid:volume_id>/", views.add_read, name="mark_as_read"),
    path("remove-read/<uuid:volume_id>/", views.remove_read, name="remove_read"),
]
from django.urls import path
from .  import views
# from .views import  SearchResultsView, ResultPageView

urlpatterns = [
    path("search/", views.search, name="search"),
]
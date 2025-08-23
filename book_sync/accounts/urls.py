from django.contrib import admin
from django.urls import path
from .  import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile_view, name="profile"),
    path("subscribe/", views.subscribe, name="subscribe"),
    path('changer-mdp/', views.change_password_view, name='change_password'),
    path('delete_user/<int:pk>/', views.delete_user, name="delete_user"),
    path('update-age-info/', views.update_age_info, name='update_age_info'),
    path('update-mature-content/', views.update_mature_content, name='update_mature_content'),
]

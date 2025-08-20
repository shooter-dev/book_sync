from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('app.urls') ),
    path('accounts/',include('accounts.urls') ),
    path('collection/',include('collection.urls') ),
    path('ma-lecture/',include('lecture.urls') ),
    path("prediction/", include("prediction.urls")),
]
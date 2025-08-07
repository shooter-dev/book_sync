from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Possession, Volume, Serie, Genre, Publisher
from django.db.models import Q


@login_required
def collection(request):
    # Récupérer les possessions de l'utilisateur
    possessions = Possession.objects.filter(user=request.user).select_related('volume__serie__genre', 'volume__serie__publisher')
    
    # Grouper par série
    series_with_volumes = {}
    for possession in possessions:
        serie = possession.volume.serie
        if serie not in series_with_volumes:
            series_with_volumes[serie] = []
        series_with_volumes[serie].append(possession)
    
    # Trier les volumes par numéro dans chaque série
    for serie, volumes in series_with_volumes.items():
        volumes.sort(key=lambda x: x.volume.number)
    
    # Statistiques
    total_books = possessions.count()
    total_series = len(series_with_volumes)
    
    context = {
        'series_with_volumes': series_with_volumes,
        'total_books': total_books,
        'total_series': total_series,
        'lus': 0,  # À implémenter plus tard
        'en_cours': 0,  # À implémenter plus tard
        'favoris': 0,  # À implémenter plus tard
    }
    
    return render(request, 'collection.html', context)

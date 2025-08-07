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
    
    # Statistiques
    total_books = possessions.count()
    
    context = {
        'possessions': possessions,
        'total_books': total_books,
        'lus': 0,  # À implémenter plus tard
        'en_cours': 0,  # À implémenter plus tard
        'favoris': 0,  # À implémenter plus tard
    }
    
    return render(request, 'collection.html', context)

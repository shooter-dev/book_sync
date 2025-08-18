from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Possession, Volume, Serie, Genre, Publisher


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
  
@csrf_exempt
def search(request):
    series = []
    search_term = ""

    if request.method == "GET" and request.GET.get('search'):
        search_term = request.GET.get('search')
        series = Serie.objects.filter(title__icontains=search_term)#.select_related('genre', 'publisher')

    context = {
        'series': series,
        'search_term': search_term,
    }
    return render(request, 'search.html', context)

@login_required
def serie_detail(request, serie_id):
    """Vue pour afficher les détails d'une série"""
    serie = get_object_or_404(Serie, id=serie_id)
    
    # Récupérer tous les volumes de la série
    volumes = Volume.objects.filter(serie=serie).order_by('number')
    
    # Récupérer les possessions de l'utilisateur pour cette série
    user_possessions = Possession.objects.filter(
        user=request.user, 
        volume__serie=serie
    ).select_related('volume')
    
    # Créer un set des IDs des volumes possédés pour un accès rapide
    possessed_volume_ids = {possession.volume.id for possession in user_possessions}
    
    # Ajouter une propriété 'possessed' à chaque volume
    for volume in volumes:
        volume.possessed = volume.id in possessed_volume_ids
    
    # Statistiques de la série
    total_volumes = volumes.count()
    possessed_volumes = len(possessed_volume_ids)
    completion_percentage = (possessed_volumes / total_volumes * 100) if total_volumes > 0 else 0
    
    context = {
        'serie': serie,
        'volumes': volumes,
        'total_volumes': total_volumes,
        'possessed_volumes': possessed_volumes,
        'completion_percentage': completion_percentage,
        'user_possessions': user_possessions,
    }
    
    return render(request, 'serie_detail.html', context)

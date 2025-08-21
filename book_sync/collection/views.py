from datetime import datetime
from pyexpat.errors import messages

from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Possession, Volume, Serie, Genre, Publisher
from django.contrib import messages

from .services import VolumeService, CollectionService


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


def serie_detail(request, serie_id):
    """Vue pour afficher les détails d'une série"""

    serie = get_object_or_404(Serie, id=serie_id)
    
    volumes = Volume.objects.filter(serie=serie).order_by('number')
    
    user_possessions = Possession.objects.filter(
        user=request.user, 
        volume__serie=serie
    ).select_related('volume')
    
    possessed_volume_ids = {possession.volume.id for possession in user_possessions}
    
    for volume in volumes:
        volume.possessed = volume.id in possessed_volume_ids
    
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


def volume_detail(request, volume_id):
    """Vue pour afficher les détails d'un volume"""

    volume = get_object_or_404(Volume, id=volume_id)
    
    user_possession = None
    try:
        user_possession = Possession.objects.get(user=request.user, volume=volume)
    except Possession.DoesNotExist:
        pass
    
    serie_volumes = Volume.objects.filter(serie=volume.serie).order_by('number')
    
    user_serie_possessions = Possession.objects.filter(
        user=request.user, 
        volume__serie=volume.serie
    ).select_related('volume')
    
    possessed_volume_ids = {possession.volume.id for possession in user_serie_possessions}
    
    for vol in serie_volumes:
        vol.possessed = vol.id in possessed_volume_ids
    
    previous_volume = None
    next_volume = None
    
    for i, vol in enumerate(serie_volumes):
        if vol.id == volume.id:
            if i > 0:
                previous_volume = serie_volumes[i - 1]
            if i < len(serie_volumes) - 1:
                next_volume = serie_volumes[i + 1]
            break
    
    total_volumes = serie_volumes.count()
    possessed_volumes = len(possessed_volume_ids)
    completion_percentage = (possessed_volumes / total_volumes * 100) if total_volumes > 0 else 0
    
    context = {
        'volume': volume,
        'user_possession': user_possession,
        'serie_volumes': serie_volumes,
        'possessed_volume_ids': possessed_volume_ids,
        'previous_volume': previous_volume,
        'next_volume': next_volume,
        'total_volumes': total_volumes,
        'possessed_volumes': possessed_volumes,
        'completion_percentage': completion_percentage,
    }
    
    return render(request, 'volume_detail.html', context)

@login_required
def add_collection(request, volume_id):
    volume = get_object_or_404(Volume, id=volume_id)
    possession_exists = Possession.objects.filter(user=request.user, volume=volume).exists()

    if not possession_exists:
        Possession.objects.create(
            user_id=request.user.id,
            volume_id=volume.id,
            created_at=datetime.now()
        )

    return redirect(request.META.get('HTTP_REFERER', 'home'))

@login_required
def delete_volume_collection(request, volume_id):
    volume = get_object_or_404(Volume, id=volume_id)
    possession_exists = Possession.objects.filter(user=request.user, volume=volume).exists()

    if possession_exists:
        Possession.objects.filter(user=request.user, volume=volume).delete()

    return redirect(request.META.get('HTTP_REFERER', 'home'))
    print("Referer:", referer)

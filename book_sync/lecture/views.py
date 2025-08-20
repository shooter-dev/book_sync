from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from collection.models import Possession
from .models import Read


@login_required
def lecture(request):
    user = request.user
    
    # Livres terminés de la collection (possédés ET lus)
    collection_read = Read.objects.filter(
        user=user,
        volume__in=Possession.objects.filter(user=user).values_list('volume', flat=True)
    ).select_related('volume__serie', 'volume__serie__publisher').order_by('volume__serie__title', 'volume__number')
    
    # Livres terminés hors collection (lus mais pas possédés)
    non_collection_read = Read.objects.filter(
        user=user
    ).exclude(
        volume__in=Possession.objects.filter(user=user).values_list('volume', flat=True)
    ).select_related('volume__serie', 'volume__serie__publisher').order_by('volume__serie__title', 'volume__number')
    
    # Volumes possédés mais pas encore lus (pile à lire de la collection)
    read_volume_ids = Read.objects.filter(user=user).values_list('volume', flat=True)
    to_read_collection = Possession.objects.filter(user=user).exclude(
        volume__in=read_volume_ids
    ).select_related('volume__serie', 'volume__serie__publisher').order_by('volume__serie__title', 'volume__number')
    
    # Calcul de la progression de collection
    total_possessed = Possession.objects.filter(user=user).count()
    total_read_collection = collection_read.count()
    
    if total_possessed > 0:
        collection_progress = round((total_read_collection / total_possessed) * 100)
    else:
        collection_progress = 0
    
    # Statistiques 
    stats = {
        'en_cours': 0,  # Pas de lectures en cours pour le moment
        'termines': Read.objects.filter(user=user).count(),
        'pile_a_lire': to_read_collection.count(),
        'progression_collection': collection_progress,
        'total_possessed': total_possessed,
        'total_read_collection': total_read_collection
    }
    
    context = {
        'collection_read': collection_read,
        'non_collection_read': non_collection_read,
        'to_read_collection': to_read_collection,
        'stats': stats,
    }
    
    return render(request, 'lecture.html', context)

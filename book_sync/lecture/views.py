from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Q
from django.contrib import messages
from django.http import HttpResponseForbidden
from collection.models import Possession, Volume
from .models import Read


def is_premium(user):
    """Vérifie si l'utilisateur fait partie du groupe premium"""
    return user.groups.filter(name='premium').exists()


@login_required
@user_passes_test(is_premium, login_url='/accounts/subscribe/')
def lecture(request):
    user: User = request.user
    
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


@login_required
@user_passes_test(is_premium, login_url='/accounts/subscribe/')
def add_read(request, volume_id):
    """Marque un volume comme lu par l'utilisateur connecté"""
    if request.method != 'POST':
        return redirect('lecture')
    
    volume = get_object_or_404(Volume, id=volume_id)
    user = request.user
    
    # Vérifier si le volume n'est pas déjà marqué comme lu
    read_entry, created = Read.objects.get_or_create(
        user=user,
        volume=volume
    )
    
    if created:
        messages.success(request, f'"{volume.serie.title} - Tome {volume.number}" a été marqué comme lu.')
    else:
        messages.info(request, f'"{volume.serie.title} - Tome {volume.number}" était déjà marqué comme lu.')
    
    return redirect('lecture')


@login_required
@user_passes_test(is_premium, login_url='/accounts/subscribe/')
def remove_read(request, volume_id):
    """Supprime une lecture d'un volume pour l'utilisateur connecté"""
    if request.method != 'POST':
        return redirect('lecture')
    
    volume = get_object_or_404(Volume, id=volume_id)
    user = request.user
    
    try:
        read_entry = Read.objects.get(user=user, volume=volume)
        read_entry.delete()
        messages.success(request, f'La lecture de "{volume.serie.title} - Tome {volume.number}" a été supprimée.')
    except Read.DoesNotExist:
        messages.error(request, f'Cette lecture n\'existe pas.')
    
    return redirect('lecture')

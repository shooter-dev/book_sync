from accounts.models import CustomUser as User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.views.decorators.http import require_POST
from collection.models import Possession, Volume
from .models import Read


def is_premium(user):
    """Vérifie si l'utilisateur a un abonnement premium"""
    return user.is_premium


@login_required
@user_passes_test(is_premium, login_url='/accounts/subscribe/')
def lecture(request):
    user: User = request.user
    
    # Optimisation : récupérer toutes les possessions de l'utilisateur
    user_possessions = set(Possession.objects.filter(user=user).values_list('volume', flat=True))
    
    # Optimisation : récupérer toutes les lectures de l'utilisateur
    user_reads = Read.objects.filter(user=user).select_related(
        'volume__serie', 'volume__serie__publisher'
    ).order_by('volume__serie__title', 'volume__number')
    
    # Séparer les lectures selon qu'elles appartiennent à la collection ou non
    collection_read = []
    non_collection_read = []
    
    for read in user_reads:
        if read.volume.id in user_possessions:
            collection_read.append(read)
        else:
            non_collection_read.append(read)
    
    # Volumes possédés mais pas encore lus (pile à lire)
    read_volume_ids = set(user_reads.values_list('volume', flat=True))
    to_read_collection = Possession.objects.filter(user=user).exclude(
        volume__id__in=read_volume_ids
    ).select_related('volume__serie', 'volume__serie__publisher').order_by('volume__serie__title', 'volume__number')
    
    # Statistiques avancées
    total_possessed = len(user_possessions)
    total_read_collection = len(collection_read)
    total_read = len(user_reads)
    total_to_read = to_read_collection.count()
    
    # Progression de collection
    collection_progress = round((total_read_collection / total_possessed) * 100) if total_possessed > 0 else 0
    
    # Statistiques par série (nouvelles)
    series_stats = {}
    for read in collection_read:
        serie_name = read.volume.serie.title
        if serie_name not in series_stats:
            series_stats[serie_name] = {'read': 0, 'total': 0}
        series_stats[serie_name]['read'] += 1
    
    # Compter le total par série
    for possession in Possession.objects.filter(user=user).select_related('volume__serie'):
        serie_name = possession.volume.serie.title
        if serie_name not in series_stats:
            series_stats[serie_name] = {'read': 0, 'total': 0}
        series_stats[serie_name]['total'] += 1
    
    # Calculer la progression par série
    for serie_name, stats in series_stats.items():
        if stats['total'] > 0:
            stats['progress'] = round((stats['read'] / stats['total']) * 100)
        else:
            stats['progress'] = 0
    
    stats = {
        'en_cours': 0,  # Fonctionnalité future
        'termines': total_read,
        'pile_a_lire': total_to_read,
        'progression_collection': collection_progress,
        'total_possessed': total_possessed,
        'total_read_collection': total_read_collection,
        'total_read_non_collection': len(non_collection_read),
        'series_stats': dict(sorted(series_stats.items()))
    }
    
    context = {
        'collection_read': collection_read,
        'non_collection_read': non_collection_read,
        'to_read_collection': to_read_collection,
        'stats': stats,
        'user_premium': True,  # Utile pour le template
    }
    
    return render(request, 'lecture.html', context)


@login_required
@user_passes_test(is_premium, login_url='/accounts/subscribe/')
@require_POST
def add_read(request, volume_id):
    """Marque un volume comme lu par l'utilisateur connecté"""
    try:
        volume = get_object_or_404(Volume, id=volume_id)
        user = request.user
        
        # Vérifier si le volume n'est pas déjà marqué comme lu
        _, created = Read.objects.get_or_create(
            user=user,
            volume=volume
        )
        
        if created:
            messages.success(request, f'"{volume.serie.title} - Tome {volume.number}" a été marqué comme lu.')
        else:
            messages.info(request, f'"{volume.serie.title} - Tome {volume.number}" était déjà marqué comme lu.')
            
    except Volume.DoesNotExist:
        messages.error(request, 'Le volume demandé n\'existe pas.')
    except Exception as e:
        messages.error(request, 'Une erreur est survenue lors de l\'ajout de la lecture.')
    
    return redirect('lecture')


@login_required
@user_passes_test(is_premium, login_url='/accounts/subscribe/')
@require_POST
def remove_read(request, volume_id):
    """Supprime une lecture d'un volume pour l'utilisateur connecté"""
    try:
        volume = get_object_or_404(Volume, id=volume_id)
        user = request.user
        
        read_entry = Read.objects.get(user=user, volume=volume)
        read_entry.delete()
        messages.success(request, f'La lecture de "{volume.serie.title} - Tome {volume.number}" a été supprimée.')
        
    except Volume.DoesNotExist:
        messages.error(request, 'Le volume demandé n\'existe pas.')
    except Read.DoesNotExist:
        messages.error(request, 'Cette lecture n\'existe pas.')
    except Exception as e:
        messages.error(request, 'Une erreur est survenue lors de la suppression de la lecture.')
    
    return redirect('lecture')

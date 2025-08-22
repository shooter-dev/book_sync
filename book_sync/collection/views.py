from datetime import datetime
from pyexpat.errors import messages

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Possession, Volume, Serie, Genre, Publisher, Kind, like_kind, like_genre
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
    """
    fonction search qui permet de trouver les série dans la BDD
    :param request:
    :return:
    """
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

def search_series(search_term):
    """
    Fonction utilitaire qui permet de réutiliser la fonction search
    :param search_term:
    :return:
    """
    if search_term:
        return Serie.objects.filter(title__icontains=search_term)
    return Serie.objects.none()

@login_required
def popup_search(request):
    """
    Fonction de recherche qui permet d'utiliser dans popup de la fonction search
    :param request:
    :return:
    """
    search_term = request.GET.get('search', '')
    series = search_series(search_term)

    return render(request, 'popup_search.html', {
        'series': series,
        'search_term': search_term,
    })


@login_required
def update_preferences(request):
    """
    Vue pour traiter les préférences de contenu (kinds et genres)
    """
    if request.method == 'POST':
        user = request.user

        # Traiter les préférences des kinds
        for key, value in request.POST.items():
            if key.startswith('kind_preference_'):
                kind_id = key.replace('kind_preference_', '')
                try:
                    kind = get_object_or_404(Kind, id=kind_id)

                    # Convertir la valeur string en boolean ou None
                    if value == 'true':
                        preference_value = True
                    elif value == 'false':
                        preference_value = False
                    else:
                        preference_value = None

                    if preference_value is not None:
                        # Créer ou mettre à jour la préférence
                        like_kind_obj, created = like_kind.objects.get_or_create(
                            user=user,
                            kind=kind,
                            defaults={'like': preference_value}
                        )
                        if not created:
                            like_kind_obj.like = preference_value
                            like_kind_obj.save()
                    else:
                        # Supprimer la préférence si elle existe
                        like_kind.objects.filter(user=user, kind=kind).delete()

                except (ValueError, Kind.DoesNotExist):
                    continue

        # Traiter les préférences des genres
        for key, value in request.POST.items():
            if key.startswith('genre_preference_'):
                genre_id = key.replace('genre_preference_', '')
                try:
                    genre = get_object_or_404(Genre, id=genre_id)

                    # Convertir la valeur string en boolean ou None
                    if value == 'true':
                        preference_value = True
                    elif value == 'false':
                        preference_value = False
                    else:
                        preference_value = None

                    if preference_value is not None:
                        # Créer ou mettre à jour la préférence
                        like_genre_obj, created = like_genre.objects.get_or_create(
                            user=user,
                            genre=genre,
                            defaults={'like': preference_value}
                        )
                        if not created:
                            like_genre_obj.like = preference_value
                            like_genre_obj.save()
                    else:
                        # Supprimer la préférence si elle existe
                        like_genre.objects.filter(user=user, genre=genre).delete()

                except (ValueError, Genre.DoesNotExist):
                    continue

        messages.success(request, 'Vos préférences de contenu ont été sauvegardées avec succès!')
        return redirect('profile')

    return redirect('profile')


@login_required
def search_content(request):
    """
    Vue AJAX pour rechercher des kinds et genres à ajouter
    """
    if request.method == 'GET':
        search_term = request.GET.get('q', '').strip()
        content_type = request.GET.get('type', '')  # 'kind' ou 'genre'

        if not search_term or content_type not in ['kind', 'genre']:
            return JsonResponse({'results': []})

        user = request.user
        results = []

        if content_type == 'kind':
            # Rechercher dans les kinds qui ne sont pas déjà dans les préférences
            existing_kind_ids = like_kind.objects.filter(user=user).values_list('kind_id', flat=True)
            kinds = Kind.objects.filter(
                title__icontains=search_term
            ).exclude(id__in=existing_kind_ids)[:10]

            for kind in kinds:
                results.append({
                    'id': str(kind.id),
                    'title': kind.title,
                    'type': 'kind'
                })

        elif content_type == 'genre':
            # Rechercher dans les genres qui ne sont pas déjà dans les préférences
            existing_genre_ids = like_genre.objects.filter(user=user).values_list('genre_id', flat=True)
            genres = Genre.objects.filter(
                title__icontains=search_term
            ).exclude(id__in=existing_genre_ids)[:10]

            for genre in genres:
                results.append({
                    'id': str(genre.id),
                    'title': genre.title,
                    'type': 'genre'
                })

        return JsonResponse({'results': results})

    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required
def add_preference(request):
    """
    Vue AJAX pour ajouter une nouvelle préférence
    """
    if request.method == 'POST':
        content_id = request.POST.get('content_id')
        content_type = request.POST.get('content_type')  # 'kind' ou 'genre'
        preference = request.POST.get('preference')  # 'true', 'false', ou 'null'

        if not content_id or content_type not in ['kind', 'genre']:
            return JsonResponse({'error': 'Paramètres invalides'}, status=400)

        # Convertir la préférence
        if preference == 'true':
            preference_value = True
        elif preference == 'false':
            preference_value = False
        else:
            preference_value = None

        user = request.user

        try:
            if content_type == 'kind':
                kind = get_object_or_404(Kind, id=content_id)
                if preference_value is not None:
                    like_kind_obj, created = like_kind.objects.get_or_create(
                        user=user,
                        kind=kind,
                        defaults={'like': preference_value}
                    )
                    if not created:
                        like_kind_obj.like = preference_value
                        like_kind_obj.save()

                    return JsonResponse({
                        'success': True,
                        'item': {
                            'id': str(kind.id),
                            'title': kind.title,
                            'userPreference': preference_value,
                            'type': 'kind'
                        }
                    })
                else:
                    like_kind.objects.filter(user=user, kind=kind).delete()
                    return JsonResponse({'success': True, 'deleted': True})

            elif content_type == 'genre':
                genre = get_object_or_404(Genre, id=content_id)
                if preference_value is not None:
                    like_genre_obj, created = like_genre.objects.get_or_create(
                        user=user,
                        genre=genre,
                        defaults={'like': preference_value}
                    )
                    if not created:
                        like_genre_obj.like = preference_value
                        like_genre_obj.save()

                    return JsonResponse({
                        'success': True,
                        'item': {
                            'id': str(genre.id),
                            'title': genre.title,
                            'userPreference': preference_value,
                            'type': 'genre'
                        }
                    })
                else:
                    like_genre.objects.filter(user=user, genre=genre).delete()
                    return JsonResponse({'success': True, 'deleted': True})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Method not allowed'}, status=405)

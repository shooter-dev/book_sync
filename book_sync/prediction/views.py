import os
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import requests
from collection.models import Kind, Possession
from collection.models import like_kind, like_genre
from lecture.models import Read
import json

def get_possessions(user_id):
    result=Possession.objects.filter(user_id=user_id).select_related("volume__serie")
    return result

def get_reads(user_id):
    result=Read.objects.filter(user_id=user_id).select_related("volume__serie")
    return result

def format_data(entries):
    result = {}
    for entry in entries:
        serie = entry.volume.serie.title
        vol_num = str(entry.volume.number)
        vol_id = str(entry.volume.id)

        if serie not in result:
            result[serie] = {
                "volumes": {},
                "id_series": str(entry.volume.serie.id)
            }

        # Volume number comme clé, ID comme valeur
        result[serie]["volumes"][vol_num] = vol_id

    return result

@login_required
def prediction_view(request):
    user_id = request.user.id

    # Données de collection et lecture
    possessions = get_possessions(user_id)
    reads = get_reads(user_id)
    collection_data = format_data(possessions)
    read_data = format_data(reads)

    # Données pour les préférences utilisateur
    from accounts.models import CustomUser
    try:
        custom_user = CustomUser.objects.get(id=request.user.id)
        user_age = custom_user.age
    except:
        user_age = None
    
    user_kind_likes = like_kind.objects.filter(user=request.user).select_related('kind')
    kinds = [like.kind for like in user_kind_likes]

    user_genres_link = like_genre.objects.filter(user=request.user).select_related('genre')
    genres = [like.genre for like in user_genres_link]

    context = {
        "collection_json": json.dumps(collection_data),
        "read_json": json.dumps(read_data),
        'user_age': user_age,
        'kinds': kinds,
        'genres': genres
    }

    return render(request, "prediction.html", context)

# def prediction_view(request):
#     """
#     Vue alternative si tu veux utiliser l'endpoint /predict-form/ de FastAPI
#     """
#     try:
#         user_id = request.user.id
#         api_url = f"{os.environ.get('URL_API_PREDICTION', 'http://localhost:8001')}/predict/"
#         # Même récupération des données
#         possessions = get_possessions(user_id)
#         reads = get_reads(user_id)
#
#         collection_data = format_data(possessions)
#         read_data = format_data(reads)
#
#         # ✅ Préparation des données pour FormData
#         form_data = {
#             'user_age': request.POST.get("user_age", "0"),
#             'user_genre': request.POST.get("user_genre", ""),
#             'genre_preference': request.POST.get("genre_preference", ""),
#             'category_preference': request.POST.get("category_preference", ""),
#             'user_comment': request.POST.get("user_comment", ""),
#             'prediction_type': request.POST.get("prediction_type", ""),
#             'collection': json.dumps(collection_data),  # ✅ JSON en string
#             'read': json.dumps(read_data)  # ✅ JSON en string
#         }
#
#         print(f"🚀 Envoi FormData vers FastAPI: {form_data}")
#
#         # ✅ Envoi en form-data
#         response = requests.post(
#             f"{os.environ.get('URL_API_PREDICTION', 'http://localhost:8001')}/predict/",
#             data=form_data,  # ✅ data=form_data pour form-encoded
#             timeout=30
#         )
#
#         if response.status_code == 200:
#             data = response.json()
#             return JsonResponse({
#                 "status": "success",
#                 "message": "Prédiction générée avec succès (FormData)",
#                 "data": data
#             })
#         else:
#             return JsonResponse({
#                 "status": "error",
#                 "message": f"Erreur API: {response.status_code}",
#                 "details": response.text
#             }, status=response.status_code)
#
#     except Exception as e:
#         print(f"❌ Erreur: {str(e)}")
#         return JsonResponse({
#             "status": "error",
#             "message": "Erreur lors de la prédiction",
#             "details": str(e)
#         }, status=500)


@login_required
def category_preference_view(request):
    user_id = request.user.id
    
    # Récupérer l'âge de l'utilisateur connecté
    from accounts.models import CustomUser
    try:
        custom_user = CustomUser.objects.get(id=request.user.id)
        user_age = custom_user.age
    except:
        user_age = None
    
    user_kind_likes = like_kind.objects.filter(user=request.user).select_related('kind')
    kinds = [like.kind for like in user_kind_likes]

    user_genres_link = like_genre.objects.filter(user=request.user).select_related('genre')
    genres = [like.genre for like in user_genres_link]
    
    # Récupération des données utilisateur
    try:
        possessions = get_possessions(user_id)
        reads = get_reads(user_id)
        
        collection_data = format_data(possessions)
        read_data = format_data(reads)
        
        collection_json = json.dumps(collection_data)
        read_json = json.dumps(read_data)
        
        # Si pas de données, utiliser des objets vides
        if not collection_data:
            collection_json = "{}"
            
        if not read_data:
            read_json = "{}"
        
    except Exception as e:
        collection_json = "{}"
        read_json = "{}"

    return render(request, 'prediction.html', {
        'user_age': user_age,
        'kinds': kinds,
        'genres': genres,
        'collection_json': collection_json,
        'read_json': read_json,
    })

@login_required
def save_age(request):
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            age = data.get('age')
            
            if age and str(age).isdigit():
                from accounts.models import CustomUser
                custom_user = CustomUser.objects.get(id=request.user.id)
                custom_user.age = int(age)
                custom_user.save()
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': 'Âge invalide'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée'})
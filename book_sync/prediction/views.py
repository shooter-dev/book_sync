import os
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import requests
from collection.models import Kind
from collection.models import like_kind, like_genre


def prediction_view(request):
    try:
        payload = {
            "user_age": int(request.GET.get("user_age", 0)),
            "user_genre": request.GET.get("user_genre", ""),
            "genre_preference": request.GET.get("genre_preference", ""),
            "category_preference": request.GET.get("category_preference", ""),
            "user_comment": request.GET.get("user_comment", ""),
            "prediction_type": request.GET.get("prediction_type", "")
        }

        response = requests.post(
            f"{os.environ.get('URL_API_PREDICTION')}/predict",
            json=payload
        )
        data = response.json()

        return JsonResponse({"prediction": data.get("data")})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
def category_preference_view(request):
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

    return render(request, 'prediction.html', {
        'user_age': user_age,
        'kinds': kinds,
        'genres': genres
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
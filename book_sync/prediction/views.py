import os
from django.shortcuts import render
from django.http import JsonResponse
import requests
from collection.models import Kind
from collection.models import like_kind
from collection.models import Genre


def prediction_view(request):
    try:
        response = requests.get(f"{ os.environ.get('URL_API_PREDICTION')}/predict")
        data = response.json()
        return JsonResponse({"prediction": data["prediction"]})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def category_preference_view(request):
    user_kind_likes = like_kind.objects.filter(user=request.user).select_related('kind')
    kinds = [like.kind for like in user_kind_likes]
    return render(request, 'prediction.html', {'kinds': kinds})


def genre_preference_view(request):
    genres = Genre.objects.all()
    print(f"Genres récupérés: {genres.count()}")

    return render(request, 'prediction.html', {'genres': genres})


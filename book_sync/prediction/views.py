import os
from django.shortcuts import render
from django.http import JsonResponse
import requests
from collection.models import Kind


def prediction_view(request):
    try:
        response = requests.get(f"{ os.environ.get('URL_API_PREDICTION')}/predict")
        data = response.json()
        return JsonResponse({"prediction": data["prediction"]})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def category_preference_view(request):
    # user_kind_likes = like_kind.objects.filter(user=request.user).select_related('kind')
    kinds = Kind.objects.all()
    return render(request, 'prediction.html', {'kinds': kinds})







#
#def category_preference_view(request):
#    kinds = Kind.objects.all()
 #   return render(request, 'prediction.html', {'kinds': kinds})

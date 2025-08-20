import os

from django.http import JsonResponse
import requests

def prediction_view(request):
    try:
        response = requests.get(f"{ os.environ.get('URL_API_PREDICTION')}/predict")
        data = response.json()
        return JsonResponse({"prediction": data["prediction"]})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
import os
from typing import Collection

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
import requests
import json
from django.http import JsonResponse
from dotenv import load_dotenv
from collection.models import Genre, Kind, Possession

load_dotenv()

def index(request):
    return render(request, 'index.html')


def collection(request):
    return render(request, 'collection.html')

def recommendation(request):
    return render(request, 'recommendation.html')

@login_required
def prediction(request):
    user_age = getattr(request.user, 'age', None)
    genres = Genre.objects.filter(to_display=True)
    kinds = Kind.objects.all()
    context = {
        'user_age': user_age,
        'genres': genres,
        'kinds': kinds,
        # 'collection_json': json.dumps(user_data['collection']),
        # 'read_json': json.dumps(user_data['read']),
    }
    return render(request, 'prediction.html', context)

@login_required
def save_age(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            age = data.get('age')
            if age is not None and str(age).isdigit():
                request.user.age = int(age)
                request.user.save(update_fields=["age"])
                return JsonResponse({'success': True, 'age': request.user.age})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Mauvaise requête'})




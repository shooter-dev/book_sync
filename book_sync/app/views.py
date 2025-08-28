import os
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
import requests
import json
from django.http import JsonResponse
from dotenv import load_dotenv
from collection.models import Genre, Kind,Possession
from typing import Collection


load_dotenv()

def is_premium(user):
    """Vérifie si l'utilisateur a un abonnement premium"""
    return user.is_premium

def index(request):
    return render(request, 'index.html')


def collection(request):
    return render(request, 'collection.html')

def recommendation(request):
    return render(request, 'recommendation.html')

@login_required
@user_passes_test(is_premium, login_url='/accounts/subscribe/')
def prediction(request):
    user_age = getattr(request.user, 'age', None)
    genres = Genre.objects.filter(to_display=True)
    kinds = Kind.objects.all()
    
    context = {
        'user_age': user_age,
        'genres': genres,
        'kinds': kinds,
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




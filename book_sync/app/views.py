import os
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
import requests
import json
from django.http import JsonResponse
from dotenv import load_dotenv
from collection.models import Genre, Kind,Possession
from core.settings import URL_API_PREDICTION

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


@login_required
@user_passes_test(is_premium, login_url='/accounts/subscribe/')
def predict_responce(request):
    """Vue pour traiter et afficher les résultats de prédiction de l'API"""

    # Initialiser les variables
    predictions = []
    user_data = {}
    api_error = None
    responce_IA_global = ""

    if request.method == 'POST':
        # Récupérer et nettoyer les données du formulaire
        user_data = {
            'age': request.POST.get('user_age', ''),
            'genre': request.POST.get('user_genre', ''),
            'mood': request.POST.get('user_mood', ''),
            'prediction_type': request.POST.get('prediction_type', ''),
            'genres': [g.strip() for g in request.POST.get('genre_preference', '').split(',') if g.strip()],
            'categories': [c.strip() for c in request.POST.get('category_preference', '').split(',') if c.strip()],
            'comment': request.POST.get('user_comment', '')
        }

        # Sauvegarder les données utilisateur dans la session
        request.session['user_prediction_data'] = user_data

        # Préparer les données pour l'API en format JSON
        try:
            collection_data = json.loads(request.POST.get('collection', '{}'))
            read_data = json.loads(request.POST.get('read', '{}'))
        except json.JSONDecodeError:
            collection_data = {}
            read_data = {}

        api_data = {
            'user_age': user_data['age'],
            'user_genre': user_data['genre'],
            'genre_preference': request.POST.get('genre_preference', ''),
            'category_preference': request.POST.get('category_preference', ''),
            'user_comment': user_data['comment'],
            'prediction_type': user_data['prediction_type'],
            'collection': collection_data,
            'read': read_data,
            'user_mood': user_data['mood']
        }

        # Appeler l'API de prédiction
        try:
            api_url = f"{URL_API_PREDICTION}/predict/"
            print(f"Envoi des données à l'API: {api_url}")
            print(f"Données envoyées: {api_data}")

            headers = {'Content-Type': 'application/json'}
            response = requests.post(api_url, json=api_data, headers=headers, timeout=60)
            print(f"Réponse API - Status: {response.status_code}")

            if response.status_code == 200:
                api_response = response.json()
                print(f"Réponse API reçue: {api_response}")

                # Récupérer les données depuis la bonne clé
                predictions = api_response.get('serie_recomendees', [])
                responce_IA_global = api_response.get('responce_IA_global', '')

                # Sauvegarder les prédictions dans la session
                request.session['predictions'] = predictions
                request.session['responce_IA_global'] = responce_IA_global

            else:
                api_error = f"Erreur API: Status {response.status_code} - {response.text}"
                print(api_error)

        except requests.exceptions.Timeout:
            api_error = "L'API de prédiction prend plus de temps que prévu. Veuillez réessayer dans quelques instants."
            print("Timeout lors de l'appel à l'API de prédiction (60s)")
        except requests.exceptions.ConnectionError:
            api_error = "Impossible de se connecter à l'API de prédiction"
            print(api_error)
        except requests.exceptions.RequestException as e:
            api_error = f"Erreur lors de l'appel à l'API: {str(e)}"
            print(api_error)
        except Exception as e:
            api_error = f"Erreur inattendue: {str(e)}"
            print(api_error)

    elif request.method == 'GET':
        # Récupérer les données depuis la session si disponibles
        predictions = request.session.get('predictions', [])
        user_data = request.session.get('user_prediction_data', {})
        responce_IA_global = request.session.get('responce_IA_global', '')

    # Préparer le contexte pour le template
    user_age = getattr(request.user, 'age', None)
    genres = Genre.objects.filter(to_display=True)
    kinds = Kind.objects.all()

    context = {
        'user_age': user_age,
        'genres': genres,
        'kinds': kinds,
        'predictions': predictions,
        'user_data': user_data,
        'api_error': api_error,
        'responce_IA_global': responce_IA_global,
    }

    return render(request, 'prediction-responce.html', context)




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

@login_required
@user_passes_test(is_premium, login_url='/accounts/subscribe/')
def predict_responce(request):
    """Vue pour traiter et afficher les résultats de prédiction de l'API"""
    
    # Initialiser les variables
    predictions = []
    user_data = {}
    api_error = None
    
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
        
        # Préparer les données pour l'API (conserver les noms de champs originaux)
        api_data = {
            'user_age': user_data['age'],
            'user_genre': user_data['genre'],
            'genre_preference': request.POST.get('genre_preference', ''),
            'category_preference': request.POST.get('category_preference', ''),
            'user_comment': user_data['comment'],
            'prediction_type': user_data['prediction_type'],
            'collection': request.POST.get('collection', '{}'),
            'read': request.POST.get('read', '{}'),
            'user_mood': user_data['mood'],
            'csrfmiddlewaretoken': request.POST.get('csrfmiddlewaretoken', '')
        }
        
        # Appeler l'API de prédiction
        try:
            api_url = "http://127.0.0.1:8001/predict/"
            print(f"Envoi des données à l'API: {api_url}")
            print(f"Données envoyées: {api_data}")
            
            response = requests.post(api_url, data=api_data, timeout=30)
            print(f"Réponse API - Status: {response.status_code}")
            
            if response.status_code == 200:
                api_response = response.json()
                print(f"Réponse API reçue: {api_response}")
                
                # Pour l'instant, l'API retourne les données de test
                # Créer des prédictions factices basées sur les préférences utilisateur
                predictions = generate_mock_predictions(user_data, api_response)
                
                # Sauvegarder les prédictions dans la session
                request.session['predictions'] = predictions
                
            else:
                api_error = f"Erreur API: Status {response.status_code} - {response.text}"
                print(api_error)
                
        except requests.exceptions.Timeout:
            api_error = "Timeout lors de l'appel à l'API de prédiction"
            print(api_error)
        except requests.exceptions.ConnectionError:
            api_error = "Impossible de se connecter à l'API de prédiction"
            print(api_error)
        except requests.exceptions.RequestException as e:
            api_error = f"Erreur lors de l'appel à l'API: {str(e)}"
            print(api_error)
        except Exception as e:
            api_error = f"Erreur inattendue: {str(e)}"
            print(api_error)
    
    # Si on accède directement à la page en GET
    elif request.method == 'GET':
        # Récupérer les données depuis la session si disponibles
        predictions = request.session.get('predictions', [])
        user_data = request.session.get('user_prediction_data', {})
    
    # Préparer le contexte pour le template
    context = {
        'predictions': predictions,
        'user_data': user_data,
        'api_error': api_error,
    }
    
    return render(request, 'prediction-responce.html', context)

def generate_mock_predictions(user_data, api_response):
    """Génère des prédictions factices basées sur les données utilisateur"""
    
    # Prédictions de base selon les préférences
    base_predictions = [
        {
            'title': 'One Piece',
            'author': 'Eiichiro Oda',
            'comment': f"Parfait pour votre humeur {user_data.get('mood', 'aventureuse')} ! Cette série d'aventure épique correspond à vos goûts.",
            'genre': user_data.get('genres', ['Aventure'])[0] if user_data.get('genres') else 'Aventure',
            'category': user_data.get('categories', ['Manga'])[0] if user_data.get('categories') else 'Manga',
            'score': 5,
            'status': 'En cours',
            'volumes_count': '100+',
            'series_id': 1
        },
        {
            'title': 'Demon Slayer',
            'author': 'Koyoharu Gotouge',
            'comment': f"Une excellente série pour quelqu'un de {user_data.get('age', '25')} ans qui apprécie l'action et l'émotion.",
            'genre': user_data.get('genres', ['Action'])[1] if len(user_data.get('genres', [])) > 1 else 'Action',
            'category': user_data.get('categories', ['Manga'])[0] if user_data.get('categories') else 'Manga',
            'score': 4,
            'status': 'Terminé',
            'volumes_count': '23',
            'series_id': 2
        },
        {
            'title': 'Spirited Away',
            'author': 'Hayao Miyazaki',
            'comment': f"Un classique du Studio Ghibli qui correspond parfaitement à votre profil {user_data.get('genre', 'passionné')} !",
            'genre': 'Fantastique',
            'category': 'Anime',
            'score': 5,
            'status': 'Film',
            'volumes_count': '1',
            'series_id': 3
        }
    ]
    
    # Filtrer selon le type de prédiction
    if user_data.get('prediction_type') == 'collection':
        # Simuler des recommandations de la collection existante
        return base_predictions[:2]
    else:
        # Propositions de découverte
        return base_predictions
        
    return base_predictions




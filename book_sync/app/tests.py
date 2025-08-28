from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from collection.models import Genre, Kind
import json

User = get_user_model()

class AppViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.premium_group = Group.objects.create(name='premium')
        
        # Créer un utilisateur premium
        self.premium_user = User.objects.create_user(
            username='premium_user',
            email='premium@test.com',
            password='testpass123',
            age=25
        )
        self.premium_user.groups.add(self.premium_group)
        
        # Créer un utilisateur normal
        self.normal_user = User.objects.create_user(
            username='normal_user',
            email='normal@test.com',
            password='testpass123',
            age=22
        )
        
        # Créer des données de test
        self.genre = Genre.objects.create(title='Action', to_display=True)
        self.hidden_genre = Genre.objects.create(title='Hidden Genre', to_display=False)
        self.kind = Kind.objects.create(title='Manga')
    
    def test_index_view(self):
        """Test de la vue index - accessible à tous"""
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'index.html')
    
    def test_collection_view(self):
        """Test de la vue collection - accessible à tous"""
        response = self.client.get(reverse('collection'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'collection.html')
    
    def test_recommendation_view(self):
        """Test de la vue recommendation - accessible à tous"""
        response = self.client.get(reverse('recommendation'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'recommendation.html')
    
    def test_prediction_view_requires_login(self):
        """Test que la vue prediction nécessite une connexion"""
        response = self.client.get(reverse('prediction'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
    
    def test_prediction_view_requires_premium(self):
        """Test que la vue prediction nécessite un statut premium"""
        self.client.login(username='normal_user', password='testpass123')
        response = self.client.get(reverse('prediction'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/subscribe/', response.url)
    
    def test_prediction_view_success_with_premium(self):
        """Test de la vue prediction avec un utilisateur premium"""
        self.client.login(username='premium_user', password='testpass123')
        response = self.client.get(reverse('prediction'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'prediction.html')
        
        # Vérifier le contexte
        self.assertIn('user_age', response.context)
        self.assertIn('genres', response.context)
        self.assertIn('kinds', response.context)
        
        # Vérifier que seuls les genres à afficher sont inclus
        genres_in_context = list(response.context['genres'])
        self.assertIn(self.genre, genres_in_context)
        self.assertNotIn(self.hidden_genre, genres_in_context)
        
        # Vérifier que tous les kinds sont inclus
        kinds_in_context = list(response.context['kinds'])
        self.assertIn(self.kind, kinds_in_context)
        
        # Vérifier l'âge utilisateur
        self.assertEqual(response.context['user_age'], 25)
    
    def test_save_age_requires_login(self):
        """Test que save_age nécessite une connexion"""
        data = {'age': 30}
        response = self.client.post(
            '/prediction/save-age/',
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
    
    def test_save_age_success(self):
        """Test de sauvegarde d'âge réussie"""
        self.client.login(username='normal_user', password='testpass123')
        
        data = {'age': 30}
        response = self.client.post(
            '/prediction/save-age/',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['age'], 30)
        
        # Vérifier que l'âge a été sauvegardé en base
        self.normal_user.refresh_from_db()
        self.assertEqual(self.normal_user.age, 30)
    
    def test_save_age_invalid_age(self):
        """Test de sauvegarde d'un âge invalide"""
        self.client.login(username='normal_user', password='testpass123')
        
        # Test avec âge non numérique
        data = {'age': 'invalid'}
        response = self.client.post(
            '/prediction/save-age/',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertIn('error', response_data)
    
    def test_save_age_negative_age(self):
        """Test de sauvegarde d'un âge négatif"""
        self.client.login(username='normal_user', password='testpass123')
        
        data = {'age': -5}
        response = self.client.post(
            '/prediction/save-age/',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertIn('error', response_data)
    
    def test_save_age_zero_age(self):
        """Test de sauvegarde d'un âge zéro"""
        self.client.login(username='normal_user', password='testpass123')
        
        data = {'age': 0}
        response = self.client.post(
            '/prediction/save-age/',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['age'], 0)
    
    def test_save_age_get_request(self):
        """Test que save_age n'accepte que les requêtes POST"""
        self.client.login(username='normal_user', password='testpass123')
        
        response = self.client.get('/prediction/save-age/')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertIn('Mauvaise requête', response_data['error'])
    
    def test_save_age_invalid_json(self):
        """Test de save_age avec JSON invalide"""
        self.client.login(username='normal_user', password='testpass123')
        
        response = self.client.post(
            '/prediction/save-age/',
            data='invalid json',
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertIn('error', response_data)

class UtilityFunctionsTestCase(TestCase):
    """Tests pour les fonctions utilitaires"""
    
    def setUp(self):
        self.premium_group = Group.objects.create(name='premium')
        
        self.premium_user = User.objects.create_user(
            username='premium_user',
            password='testpass123'
        )
        self.premium_user.groups.add(self.premium_group)
        
        self.normal_user = User.objects.create_user(
            username='normal_user',
            password='testpass123'
        )
    
    def test_is_premium_function_with_premium_user(self):
        """Test de la fonction is_premium avec un utilisateur premium"""
        from app.views import is_premium
        
        self.assertTrue(is_premium(self.premium_user))
    
    def test_is_premium_function_with_normal_user(self):
        """Test de la fonction is_premium avec un utilisateur normal"""
        from app.views import is_premium
        
        self.assertFalse(is_premium(self.normal_user))
    
    def test_prediction_view_user_without_age(self):
        """Test de la vue prediction avec un utilisateur sans âge défini"""
        user_no_age = User.objects.create_user(
            username='no_age_user',
            password='testpass123'
        )
        user_no_age.groups.add(self.premium_group)
        
        client = Client()
        client.login(username='no_age_user', password='testpass123')
        
        response = client.get(reverse('prediction'))
        
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context['user_age'])
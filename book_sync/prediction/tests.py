from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from collection.models import Genre, Kind, Possession, like_kind, like_genre, Volume, Serie
from lecture.models import Read
import json

User = get_user_model()

class PredictionViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.premium_group = Group.objects.create(name='premium')
        
        # Créer un utilisateur premium
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123',
            age=25
        )
        self.user.groups.add(self.premium_group)
        
        # Créer des données de test
        self.genre = Genre.objects.create(title='Science Fiction', to_display=True)
        self.kind = Kind.objects.create(title='Manga')
        
        self.serie = Serie.objects.create(
            title='Test Serie',
            description='Test description'
        )
        
        self.volume = Volume.objects.create(
            serie=self.serie,
            number=1,
            title='Volume 1'
        )
        
        # Créer des préférences utilisateur
        like_genre.objects.create(user=self.user, genre=self.genre)
        like_kind.objects.create(user=self.user, kind=self.kind)
        
        # Créer une possession et une lecture
        Possession.objects.create(user=self.user, volume=self.volume)
        Read.objects.create(user=self.user, volume=self.volume)
    
    def test_prediction_view_requires_login(self):
        """Test que la vue de prédiction nécessite une connexion"""
        response = self.client.get('/prediction/prediction-view/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
    
    def test_prediction_view_requires_premium(self):
        """Test que la vue de prédiction nécessite un abonnement premium"""
        # Créer un utilisateur non-premium
        regular_user = User.objects.create_user(
            username='regular',
            password='testpass123'
        )
        self.client.login(username='regular', password='testpass123')
        
        response = self.client.get('/prediction/prediction-view/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/subscribe/', response.url)
    
    def test_prediction_view_success_with_premium_user(self):
        """Test que la vue de prédiction fonctionne pour un utilisateur premium"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get('/prediction/prediction-view/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Prédiction de votre prochaine lecture')
        
        # Vérifier que les données sont dans le contexte
        self.assertIn('collection_json', response.context)
        self.assertIn('read_json', response.context)
        self.assertIn('user_age', response.context)
        self.assertIn('kinds', response.context)
        self.assertIn('genres', response.context)
        
        # Vérifier les données JSON
        collection_data = json.loads(response.context['collection_json'])
        read_data = json.loads(response.context['read_json'])
        
        self.assertIn('Test Serie', collection_data)
        self.assertIn('Test Serie', read_data)
    
    def test_save_age_view(self):
        """Test de la sauvegarde de l'âge"""
        self.client.login(username='testuser', password='testpass123')
        
        data = {'age': 30}
        response = self.client.post(
            '/prediction/save-age/',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        
        # Vérifier que l'âge a été sauvegardé
        self.user.refresh_from_db()
        self.assertEqual(self.user.age, 30)
    
    def test_save_age_invalid_data(self):
        """Test de la sauvegarde d'un âge invalide"""
        self.client.login(username='testuser', password='testpass123')
        
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
    
    def test_get_possessions_function(self):
        """Test de la fonction get_possessions"""
        from prediction.views import get_possessions
        
        possessions = get_possessions(self.user.id)
        self.assertEqual(possessions.count(), 1)
        self.assertEqual(possessions.first().volume.title, 'Volume 1')
    
    def test_get_reads_function(self):
        """Test de la fonction get_reads"""
        from prediction.views import get_reads
        
        reads = get_reads(self.user.id)
        self.assertEqual(reads.count(), 1)
        self.assertEqual(reads.first().volume.title, 'Volume 1')
    
    def test_format_data_function(self):
        """Test de la fonction format_data"""
        from prediction.views import format_data, get_possessions
        
        possessions = get_possessions(self.user.id)
        formatted_data = format_data(possessions)
        
        self.assertIn('Test Serie', formatted_data)
        self.assertIn('volumes', formatted_data['Test Serie'])
        self.assertIn('id_series', formatted_data['Test Serie'])
        self.assertIn('1', formatted_data['Test Serie']['volumes'])
        self.assertEqual(
            formatted_data['Test Serie']['volumes']['1'],
            str(self.volume.id)
        )
    
    def test_category_preference_view_without_data(self):
        """Test de la vue category_preference sans données"""
        # Créer un utilisateur sans données
        user_no_data = User.objects.create_user(
            username='nodata',
            password='testpass123'
        )
        user_no_data.groups.add(self.premium_group)
        
        self.client.login(username='nodata', password='testpass123')
        
        response = self.client.get('/prediction/category-preference-view/')
        self.assertEqual(response.status_code, 200)
        
        # Vérifier que les données JSON sont des objets vides
        self.assertEqual(response.context['collection_json'], '{}')
        self.assertEqual(response.context['read_json'], '{}')

class PredictionUtilsTestCase(TestCase):
    """Tests pour les fonctions utilitaires de prédiction"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            age=25
        )
        
        self.serie = Serie.objects.create(
            title='Test Serie',
            description='Test description'
        )
        
        self.volume1 = Volume.objects.create(
            serie=self.serie,
            number=1,
            title='Volume 1'
        )
        
        self.volume2 = Volume.objects.create(
            serie=self.serie,
            number=2,
            title='Volume 2'
        )
    
    def test_format_data_multiple_volumes(self):
        """Test du formatage de données avec plusieurs volumes"""
        from prediction.views import format_data
        
        # Créer des possessions multiples
        possession1 = Possession.objects.create(user=self.user, volume=self.volume1)
        possession2 = Possession.objects.create(user=self.user, volume=self.volume2)
        
        possessions = [possession1, possession2]
        formatted_data = format_data(possessions)
        
        self.assertIn('Test Serie', formatted_data)
        volumes = formatted_data['Test Serie']['volumes']
        
        self.assertIn('1', volumes)
        self.assertIn('2', volumes)
        self.assertEqual(volumes['1'], str(self.volume1.id))
        self.assertEqual(volumes['2'], str(self.volume2.id))
    
    def test_format_data_empty_list(self):
        """Test du formatage de données avec une liste vide"""
        from prediction.views import format_data
        
        formatted_data = format_data([])
        self.assertEqual(formatted_data, {})
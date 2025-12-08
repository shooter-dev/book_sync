from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.messages import get_messages
from collection.models import Genre, Publisher, Serie, Volume, Possession
from .models import Read
import uuid

User = get_user_model()

class ReadModelTestCase(TestCase):
    """Tests pour le modèle Read"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        
        # Créer des données de test
        publisher = Publisher.objects.create(title="Test Publisher")
        genre = Genre.objects.create(title="Test Genre")
        serie = Serie.objects.create(
            title="Test Serie",
            publisher=publisher,
            genre=genre
        )
        
        self.volume = Volume.objects.create(
            title="Test Volume",
            number=1,
            serie=serie
        )
    
    def test_read_creation(self):
        """Test de création d'une lecture"""
        read = Read.objects.create(
            user=self.user,
            volume=self.volume
        )
        
        self.assertEqual(str(read), f"{self.user.username} a lu {self.volume}")
        self.assertEqual(read.user, self.user)
        self.assertEqual(read.volume, self.volume)
        self.assertIsNotNone(read.created_at)
        self.assertIsInstance(read.id, uuid.UUID)
    
    def test_read_unique_constraint(self):
        """Test de contrainte d'unicité pour les lectures"""
        Read.objects.create(user=self.user, volume=self.volume)
        
        # Tenter de créer une seconde lecture identique
        with self.assertRaises(Exception):
            Read.objects.create(user=self.user, volume=self.volume)
    
    def test_read_ordering(self):
        """Test de l'ordre des lectures (plus récent en premier)"""
        # Créer un second volume
        volume2 = Volume.objects.create(
            title="Volume 2",
            number=2,
            serie=self.volume.serie
        )
        
        read1 = Read.objects.create(user=self.user, volume=self.volume)
        read2 = Read.objects.create(user=self.user, volume=volume2)
        
        reads = list(Read.objects.all())
        self.assertEqual(reads[0], read2)  # Plus récent en premier
        self.assertEqual(reads[1], read1)
    
    def test_read_cascade_protection(self):
        """Test de protection en cascade"""
        read = Read.objects.create(user=self.user, volume=self.volume)
        
        # Vérifier que la suppression de l'utilisateur est protégée
        with self.assertRaises(Exception):
            self.user.delete()
        
        # Vérifier que la suppression du volume est protégée
        with self.assertRaises(Exception):
            self.volume.delete()

class LectureViewsTestCase(TestCase):
    """Tests pour les vues de lecture"""
    
    def setUp(self):
        self.client = Client()
        
        # Créer les groupes
        self.user_group = Group.objects.create(name='user')
        self.premium_group = Group.objects.create(name='premium')
        
        # Créer un utilisateur premium
        self.premium_user = User.objects.create_user(
            username="premium_user",
            password="testpass123"
        )
        self.premium_user.groups.add(self.premium_group)
        
        # Créer un utilisateur normal
        self.normal_user = User.objects.create_user(
            username="normal_user",
            password="testpass123"
        )
        self.normal_user.groups.add(self.user_group)
        
        # Créer des données de test
        publisher = Publisher.objects.create(title="Test Publisher")
        genre = Genre.objects.create(title="Test Genre")
        
        self.serie = Serie.objects.create(
            title="Test Serie",
            publisher=publisher,
            genre=genre
        )
        
        # Créer plusieurs volumes
        self.volumes = []
        for i in range(1, 4):
            volume = Volume.objects.create(
                title=f"Volume {i}",
                number=i,
                serie=self.serie
            )
            self.volumes.append(volume)
        
        # Créer des possessions pour l'utilisateur premium
        for volume in self.volumes:
            Possession.objects.create(user=self.premium_user, volume=volume)
        
        # Marquer certains volumes comme lus
        Read.objects.create(user=self.premium_user, volume=self.volumes[0])  # Volume 1
        Read.objects.create(user=self.premium_user, volume=self.volumes[1])  # Volume 2
    
    def test_lecture_view_requires_login(self):
        """Test que la vue lecture nécessite une connexion"""
        response = self.client.get('/ma-lecture/lecture/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
    
    def test_lecture_view_requires_premium(self):
        """Test que la vue lecture nécessite un statut premium"""
        self.client.login(username='normal_user', password='testpass123')
        response = self.client.get('/ma-lecture/lecture/')
        
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/subscribe/', response.url)
    
    def test_lecture_view_success_with_premium(self):
        """Test de la vue lecture avec un utilisateur premium"""
        self.client.login(username='premium_user', password='testpass123')
        response = self.client.get('/ma-lecture/lecture/')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'lecture.html')
        
        # Vérifier le contexte
        self.assertIn('collection_read', response.context)
        self.assertIn('non_collection_read', response.context)
        self.assertIn('to_read_collection', response.context)
        self.assertIn('stats', response.context)
        
        # Vérifier les statistiques
        stats = response.context['stats']
        self.assertEqual(stats['total_possessed'], 3)
        self.assertEqual(stats['total_read_collection'], 2)
        self.assertEqual(stats['pile_a_lire'], 1)  # Volume 3 pas encore lu
        self.assertEqual(stats['progression_collection'], 67)  # 2/3 * 100 arrondi
        
        # Vérifier les lectures de collection
        collection_read = list(response.context['collection_read'])
        self.assertEqual(len(collection_read), 2)
        
        # Vérifier la pile à lire
        to_read = list(response.context['to_read_collection'])
        self.assertEqual(len(to_read), 1)
        self.assertEqual(to_read[0].volume, self.volumes[2])  # Volume 3
    
    def test_add_read_requires_login(self):
        """Test que add_read nécessite une connexion"""
        response = self.client.post(f'/ma-lecture/add-read/{self.volumes[0].id}/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
    
    def test_add_read_requires_premium(self):
        """Test que add_read nécessite un statut premium"""
        self.client.login(username='normal_user', password='testpass123')
        response = self.client.post(f'/ma-lecture/add-read/{self.volumes[0].id}/')
        
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/subscribe/', response.url)
    
    def test_add_read_success(self):
        """Test d'ajout de lecture réussi"""
        self.client.login(username='premium_user', password='testpass123')
        
        # Ajouter une lecture pour le volume 3 (non encore lu)
        response = self.client.post(f'/ma-lecture/add-read/{self.volumes[2].id}/')
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/ma-lecture/lecture/')
        
        # Vérifier que la lecture a été ajoutée
        self.assertTrue(Read.objects.filter(
            user=self.premium_user,
            volume=self.volumes[2]
        ).exists())
        
        # Vérifier les messages de succès
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('marqué comme lu' in str(m) for m in messages))
    
    def test_add_read_already_read(self):
        """Test d'ajout d'une lecture déjà existante"""
        self.client.login(username='premium_user', password='testpass123')
        
        # Essayer d'ajouter une lecture pour le volume 1 (déjà lu)
        response = self.client.post(f'/ma-lecture/add-read/{self.volumes[0].id}/')
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/ma-lecture/lecture/')
        
        # Vérifier les messages d'info
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('déjà marqué comme lu' in str(m) for m in messages))
    
    def test_add_read_nonexistent_volume(self):
        """Test d'ajout de lecture pour un volume inexistant"""
        self.client.login(username='premium_user', password='testpass123')
        
        fake_id = uuid.uuid4()
        response = self.client.post(f'/ma-lecture/add-read/{fake_id}/')
        
        self.assertEqual(response.status_code, 404)
    
    def test_add_read_get_method_not_allowed(self):
        """Test que add_read n'accepte que les requêtes POST"""
        self.client.login(username='premium_user', password='testpass123')
        
        response = self.client.get(f'/ma-lecture/add-read/{self.volumes[0].id}/')
        self.assertEqual(response.status_code, 405)  # Method Not Allowed
    
    def test_remove_read_success(self):
        """Test de suppression de lecture réussi"""
        self.client.login(username='premium_user', password='testpass123')
        
        # Supprimer la lecture du volume 1
        response = self.client.post(f'/ma-lecture/remove-read/{self.volumes[0].id}/')
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/ma-lecture/lecture/')
        
        # Vérifier que la lecture a été supprimée
        self.assertFalse(Read.objects.filter(
            user=self.premium_user,
            volume=self.volumes[0]
        ).exists())
        
        # Vérifier les messages de succès
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('supprimée' in str(m) for m in messages))
    
    def test_remove_read_nonexistent_read(self):
        """Test de suppression d'une lecture inexistante"""
        self.client.login(username='premium_user', password='testpass123')
        
        # Essayer de supprimer la lecture du volume 3 (pas encore lu)
        response = self.client.post(f'/ma-lecture/remove-read/{self.volumes[2].id}/')
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/ma-lecture/lecture/')
        
        # Vérifier les messages d'erreur
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("n'existe pas" in str(m) for m in messages))
    
    def test_remove_read_nonexistent_volume(self):
        """Test de suppression de lecture pour un volume inexistant"""
        self.client.login(username='premium_user', password='testpass123')
        
        fake_id = uuid.uuid4()
        response = self.client.post(f'/ma-lecture/remove-read/{fake_id}/')
        
        self.assertEqual(response.status_code, 404)

class LectureStatisticsTestCase(TestCase):
    """Tests pour les statistiques de lecture"""
    
    def setUp(self):
        self.client = Client()
        self.premium_group = Group.objects.create(name='premium')
        
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        self.user.groups.add(self.premium_group)
        
        # Créer des données de test plus complexes
        publisher = Publisher.objects.create(title="Test Publisher")
        genre = Genre.objects.create(title="Test Genre")
        
        # Créer deux séries
        self.serie1 = Serie.objects.create(
            title="Serie 1",
            publisher=publisher,
            genre=genre
        )
        
        self.serie2 = Serie.objects.create(
            title="Serie 2",
            publisher=publisher,
            genre=genre
        )
        
        # Créer des volumes pour chaque série
        self.volumes_serie1 = []
        for i in range(1, 4):  # 3 volumes pour série 1
            volume = Volume.objects.create(
                title=f"Volume {i}",
                number=i,
                serie=self.serie1
            )
            self.volumes_serie1.append(volume)
            Possession.objects.create(user=self.user, volume=volume)
        
        self.volumes_serie2 = []
        for i in range(1, 3):  # 2 volumes pour série 2
            volume = Volume.objects.create(
                title=f"Volume {i}",
                number=i,
                serie=self.serie2
            )
            self.volumes_serie2.append(volume)
            Possession.objects.create(user=self.user, volume=volume)
        
        # Marquer certains volumes comme lus
        # Série 1: 2/3 volumes lus
        Read.objects.create(user=self.user, volume=self.volumes_serie1[0])
        Read.objects.create(user=self.user, volume=self.volumes_serie1[1])
        
        # Série 2: 1/2 volumes lus
        Read.objects.create(user=self.user, volume=self.volumes_serie2[0])
    
    def test_statistics_calculation(self):
        """Test du calcul des statistiques"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/ma-lecture/lecture/')
        
        stats = response.context['stats']
        
        # Statistiques générales
        self.assertEqual(stats['total_possessed'], 5)  # 3 + 2 volumes
        self.assertEqual(stats['total_read_collection'], 3)  # 2 + 1 lectures
        self.assertEqual(stats['pile_a_lire'], 2)  # 5 - 3 volumes non lus
        self.assertEqual(stats['progression_collection'], 60)  # 3/5 * 100
        
        # Statistiques par série
        series_stats = stats['series_stats']
        
        # Série 1: 2/3 = 67%
        self.assertEqual(series_stats['Serie 1']['read'], 2)
        self.assertEqual(series_stats['Serie 1']['total'], 3)
        self.assertEqual(series_stats['Serie 1']['progress'], 67)
        
        # Série 2: 1/2 = 50%
        self.assertEqual(series_stats['Serie 2']['read'], 1)
        self.assertEqual(series_stats['Serie 2']['total'], 2)
        self.assertEqual(series_stats['Serie 2']['progress'], 50)
    
    def test_empty_collection_statistics(self):
        """Test des statistiques avec une collection vide"""
        # Créer un nouvel utilisateur sans possessions
        empty_user = User.objects.create_user(
            username="empty_user",
            password="testpass123"
        )
        empty_user.groups.add(self.premium_group)
        
        self.client.login(username='empty_user', password='testpass123')
        response = self.client.get('/ma-lecture/lecture/')
        
        stats = response.context['stats']
        
        self.assertEqual(stats['total_possessed'], 0)
        self.assertEqual(stats['total_read_collection'], 0)
        self.assertEqual(stats['pile_a_lire'], 0)
        self.assertEqual(stats['progression_collection'], 0)
        self.assertEqual(len(stats['series_stats']), 0)

class LectureIntegrationTestCase(TestCase):
    """Tests d'intégration pour le module lecture"""
    
    def setUp(self):
        self.client = Client()
        self.premium_group = Group.objects.create(name='premium')
        
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        self.user.groups.add(self.premium_group)
        
        # Créer des données complètes
        publisher = Publisher.objects.create(title="Shogakukan")
        genre = Genre.objects.create(title="Adventure")
        
        self.serie = Serie.objects.create(
            title="One Piece",
            publisher=publisher,
            genre=genre
        )
        
        # Créer 5 volumes
        self.volumes = []
        for i in range(1, 6):
            volume = Volume.objects.create(
                title=f"Volume {i}",
                number=i,
                serie=self.serie
            )
            self.volumes.append(volume)
            Possession.objects.create(user=self.user, volume=volume)
    
    def test_complete_reading_workflow(self):
        """Test du workflow complet de lecture"""
        self.client.login(username='testuser', password='testpass123')
        
        # 1. État initial - aucun volume lu
        response = self.client.get('/ma-lecture/lecture/')
        stats = response.context['stats']
        
        self.assertEqual(stats['total_read_collection'], 0)
        self.assertEqual(stats['pile_a_lire'], 5)
        self.assertEqual(stats['progression_collection'], 0)
        
        # 2. Marquer les volumes 1, 2, 3 comme lus
        for i in range(3):
            response = self.client.post(f'/ma-lecture/add-read/{self.volumes[i].id}/')
            self.assertEqual(response.status_code, 302)
        
        # 3. Vérifier les nouvelles statistiques
        response = self.client.get('/ma-lecture/lecture/')
        stats = response.context['stats']
        
        self.assertEqual(stats['total_read_collection'], 3)
        self.assertEqual(stats['pile_a_lire'], 2)
        self.assertEqual(stats['progression_collection'], 60)  # 3/5 * 100
        
        # Vérifier les lectures dans la collection
        collection_read = list(response.context['collection_read'])
        self.assertEqual(len(collection_read), 3)
        
        # Vérifier la pile à lire
        to_read = list(response.context['to_read_collection'])
        self.assertEqual(len(to_read), 2)
        
        # 4. Supprimer une lecture
        response = self.client.post(f'/ma-lecture/remove-read/{self.volumes[1].id}/')
        self.assertEqual(response.status_code, 302)
        
        # 5. Vérifier les statistiques après suppression
        response = self.client.get('/ma-lecture/lecture/')
        stats = response.context['stats']
        
        self.assertEqual(stats['total_read_collection'], 2)
        self.assertEqual(stats['pile_a_lire'], 3)
        self.assertEqual(stats['progression_collection'], 40)  # 2/5 * 100
        
        # Vérifier que le volume 2 n'est plus dans les lectures
        collection_read = list(response.context['collection_read'])
        read_volume_numbers = [read.volume.number for read in collection_read]
        self.assertNotIn(2, read_volume_numbers)
        self.assertIn(1, read_volume_numbers)
        self.assertIn(3, read_volume_numbers)
    
    def test_reading_volumes_not_in_collection(self):
        """Test de lecture de volumes non possédés"""
        # Créer un volume non possédé
        non_owned_volume = Volume.objects.create(
            title="Volume Non Possédé",
            number=10,
            serie=self.serie
        )
        
        # Marquer ce volume comme lu
        Read.objects.create(user=self.user, volume=non_owned_volume)
        
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/ma-lecture/lecture/')
        
        # Vérifier que ce volume apparaît dans non_collection_read
        non_collection_read = list(response.context['non_collection_read'])
        self.assertEqual(len(non_collection_read), 1)
        self.assertEqual(non_collection_read[0].volume, non_owned_volume)
        
        # Vérifier les statistiques
        stats = response.context['stats']
        self.assertEqual(stats['total_read_non_collection'], 1)

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
    
    def test_is_premium_function(self):
        """Test de la fonction is_premium"""
        from lecture.views import is_premium
        
        self.assertTrue(is_premium(self.premium_user))
        self.assertFalse(is_premium(self.normal_user))
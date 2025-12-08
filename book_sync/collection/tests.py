from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.utils import timezone
from .models import (
    Authors, Genre, Kind, Publisher, Serie, Volume, 
    Possession, Jobs, Tasks, like_kind, like_genre
)
from .services import VolumeService, CollectionService
import uuid
from datetime import date

User = get_user_model()

class AuthorsModelTestCase(TestCase):
    """Tests pour le modèle Authors"""
    
    def test_author_creation_with_first_name(self):
        """Test de création d'auteur avec prénom"""
        author = Authors.objects.create(
            name="Toriyama",
            first_name="Akira"
        )
        
        self.assertEqual(str(author), "Toriyama Akira")
        self.assertEqual(repr(author), "Toriyama Akira")
    
    def test_author_creation_without_first_name(self):
        """Test de création d'auteur sans prénom"""
        author = Authors.objects.create(name="Toriyama")
        
        self.assertEqual(str(author), "Toriyama")
        self.assertEqual(repr(author), "Toriyama")
    
    def test_author_uuid_field(self):
        """Test que l'ID est un UUID"""
        author = Authors.objects.create(name="Test Author")
        
        self.assertIsInstance(author.id, uuid.UUID)

class GenreModelTestCase(TestCase):
    """Tests pour le modèle Genre"""
    
    def test_genre_creation(self):
        """Test de création de genre"""
        genre = Genre.objects.create(title="Action")
        
        self.assertEqual(str(genre), "Action")
        self.assertEqual(repr(genre), "Action")
        self.assertTrue(genre.to_display)
    
    def test_genre_to_display_false(self):
        """Test de genre non affiché"""
        genre = Genre.objects.create(title="Hidden", to_display=False)
        
        self.assertFalse(genre.to_display)
    
    def test_genre_ordering(self):
        """Test de l'ordre des genres"""
        Genre.objects.create(title="Z Genre")
        Genre.objects.create(title="A Genre")
        
        genres = list(Genre.objects.all())
        self.assertEqual(genres[0].title, "A Genre")
        self.assertEqual(genres[1].title, "Z Genre")

class KindModelTestCase(TestCase):
    """Tests pour le modèle Kind"""
    
    def test_kind_creation(self):
        """Test de création de kind"""
        kind = Kind.objects.create(title="Manga")
        
        self.assertEqual(str(kind), "Manga")
        self.assertEqual(repr(kind), "Manga")
        self.assertIsInstance(kind.id, uuid.UUID)
    
    def test_kind_ordering(self):
        """Test de l'ordre des kinds"""
        Kind.objects.create(title="Z Kind")
        Kind.objects.create(title="A Kind")
        
        kinds = list(Kind.objects.all())
        self.assertEqual(kinds[0].title, "A Kind")
        self.assertEqual(kinds[1].title, "Z Kind")

class PublisherModelTestCase(TestCase):
    """Tests pour le modèle Publisher"""
    
    def test_publisher_creation(self):
        """Test de création d'éditeur"""
        publisher = Publisher.objects.create(title="Shogakukan")
        
        self.assertEqual(str(publisher), "Shogakukan")
        self.assertEqual(repr(publisher), "Shogakukan")

class SerieModelTestCase(TestCase):
    """Tests pour le modèle Serie"""
    
    def setUp(self):
        self.publisher = Publisher.objects.create(title="Test Publisher")
        self.genre = Genre.objects.create(title="Test Genre")
        self.kind1 = Kind.objects.create(title="Manga")
        self.kind2 = Kind.objects.create(title="Light Novel")
    
    def test_serie_creation(self):
        """Test de création de série"""
        serie = Serie.objects.create(
            title="One Piece",
            publisher=self.publisher,
            genre=self.genre
        )
        
        self.assertEqual(str(serie), "One Piece")
        self.assertEqual(repr(serie), "One Piece")
        self.assertFalse(serie.adult_content)
    
    def test_serie_with_adult_content(self):
        """Test de série avec contenu adulte"""
        serie = Serie.objects.create(
            title="Adult Serie",
            adult_content=True,
            publisher=self.publisher,
            genre=self.genre
        )
        
        self.assertTrue(serie.adult_content)
    
    def test_serie_with_kinds(self):
        """Test de série avec types de contenu"""
        serie = Serie.objects.create(
            title="Multi-Kind Serie",
            publisher=self.publisher,
            genre=self.genre
        )
        
        serie.kinds.add(self.kind1, self.kind2)
        
        self.assertEqual(serie.kinds.count(), 2)
        self.assertIn(self.kind1, serie.kinds.all())
        self.assertIn(self.kind2, serie.kinds.all())

class VolumeModelTestCase(TestCase):
    """Tests pour le modèle Volume"""
    
    def setUp(self):
        self.publisher = Publisher.objects.create(title="Test Publisher")
        self.genre = Genre.objects.create(title="Test Genre")
        self.serie = Serie.objects.create(
            title="Test Serie",
            publisher=self.publisher,
            genre=self.genre
        )
    
    def test_volume_creation(self):
        """Test de création de volume"""
        volume = Volume.objects.create(
            title="Volume 1",
            number=1,
            serie=self.serie
        )
        
        self.assertEqual(str(volume), "Volume 1")
        self.assertEqual(volume.number, 1)
        self.assertEqual(volume.possessions_count, 0)
        self.assertEqual(volume.image_url, "cover.png")
        self.assertEqual(volume.content, "...")
    
    def test_volume_with_details(self):
        """Test de volume avec détails complets"""
        volume = Volume.objects.create(
            title="Volume Détaillé",
            number=5,
            release_date=date(2023, 1, 15),
            isbn="978-2-123456-78-9",
            image_url="custom_cover.jpg",
            content="Résumé du volume",
            serie=self.serie
        )
        
        self.assertEqual(volume.release_date, date(2023, 1, 15))
        self.assertEqual(volume.isbn, "978-2-123456-78-9")
        self.assertEqual(volume.image_url, "custom_cover.jpg")
        self.assertEqual(volume.content, "Résumé du volume")
    
    def test_volume_ordering(self):
        """Test de l'ordre des volumes"""
        volume2 = Volume.objects.create(title="Volume 2", number=2, serie=self.serie)
        volume1 = Volume.objects.create(title="Volume 1", number=1, serie=self.serie)
        
        volumes = list(Volume.objects.all())
        self.assertEqual(volumes[0], volume1)
        self.assertEqual(volumes[1], volume2)

class PossessionModelTestCase(TestCase):
    """Tests pour le modèle Possession"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        
        publisher = Publisher.objects.create(title="Test Publisher")
        genre = Genre.objects.create(title="Test Genre")
        serie = Serie.objects.create(
            title="Test Serie",
            publisher=publisher,
            genre=genre
        )
        
        self.volume = Volume.objects.create(
            title="Test Volume",
            serie=serie
        )
    
    def test_possession_creation(self):
        """Test de création de possession"""
        possession = Possession.objects.create(
            user=self.user,
            volume=self.volume
        )
        
        self.assertEqual(str(possession), f"{self.user.username} possède {self.volume}")
        self.assertEqual(possession.user, self.user)
        self.assertEqual(possession.volume, self.volume)
        self.assertIsNotNone(possession.created_at)
    
    def test_possession_unique_constraint(self):
        """Test de contrainte d'unicité possession"""
        Possession.objects.create(user=self.user, volume=self.volume)
        
        # Tenter de créer une seconde possession identique
        with self.assertRaises(Exception):
            Possession.objects.create(user=self.user, volume=self.volume)
    
    def test_possession_ordering(self):
        """Test de l'ordre des possessions (plus récent en premier)"""
        possession1 = Possession.objects.create(user=self.user, volume=self.volume)
        
        # Créer un autre volume et une autre possession
        volume2 = Volume.objects.create(title="Volume 2", serie=self.volume.serie)
        possession2 = Possession.objects.create(user=self.user, volume=volume2)
        
        possessions = list(Possession.objects.all())
        self.assertEqual(possessions[0], possession2)  # Plus récent en premier
        self.assertEqual(possessions[1], possession1)

class LikeKindModelTestCase(TestCase):
    """Tests pour le modèle like_kind"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        self.kind = Kind.objects.create(title="Manga")
    
    def test_like_kind_creation_positive(self):
        """Test de création de like_kind positif"""
        like = like_kind.objects.create(
            user=self.user,
            kind=self.kind,
            like=True
        )
        
        self.assertEqual(str(like), f"{self.user.username} aime {self.kind.title}")
        self.assertTrue(like.like)
    
    def test_like_kind_creation_negative(self):
        """Test de création de like_kind négatif"""
        like = like_kind.objects.create(
            user=self.user,
            kind=self.kind,
            like=False
        )
        
        self.assertEqual(str(like), f"{self.user.username} n'aime pas {self.kind.title}")
        self.assertFalse(like.like)
    
    def test_like_kind_unique_constraint(self):
        """Test de contrainte d'unicité like_kind"""
        like_kind.objects.create(user=self.user, kind=self.kind)
        
        # Tenter de créer un second like identique
        with self.assertRaises(Exception):
            like_kind.objects.create(user=self.user, kind=self.kind)

class LikeGenreModelTestCase(TestCase):
    """Tests pour le modèle like_genre"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        self.genre = Genre.objects.create(title="Action")
    
    def test_like_genre_creation_positive(self):
        """Test de création de like_genre positif"""
        like = like_genre.objects.create(
            user=self.user,
            genre=self.genre,
            like=True
        )
        
        self.assertEqual(str(like), f"{self.user.username} aime {self.genre.title}")
        self.assertTrue(like.like)
    
    def test_like_genre_creation_negative(self):
        """Test de création de like_genre négatif"""
        like = like_genre.objects.create(
            user=self.user,
            genre=self.genre,
            like=False
        )
        
        self.assertEqual(str(like), f"{self.user.username} n'aime pas {self.genre.title}")
        self.assertFalse(like.like)

class JobsTasksModelTestCase(TestCase):
    """Tests pour les modèles Jobs et Tasks"""
    
    def setUp(self):
        self.author = Authors.objects.create(name="Test Author")
        self.job = Jobs.objects.create(title="Scénariste")
        
        publisher = Publisher.objects.create(title="Test Publisher")
        genre = Genre.objects.create(title="Test Genre")
        self.serie = Serie.objects.create(
            title="Test Serie",
            publisher=publisher,
            genre=genre
        )
    
    def test_jobs_creation(self):
        """Test de création de job"""
        self.assertEqual(str(self.job), "Scénariste")
        self.assertIsInstance(self.job.id, uuid.UUID)
    
    def test_jobs_unique_constraint(self):
        """Test de contrainte d'unicité des jobs"""
        with self.assertRaises(Exception):
            Jobs.objects.create(title="Scénariste")  # Même titre
    
    def test_tasks_creation(self):
        """Test de création de task"""
        task = Tasks.objects.create(
            id_author=self.author,
            id_jobs=self.job,
            id_serie=self.serie
        )
        
        self.assertEqual(task.id_author, self.author)
        self.assertEqual(task.id_jobs, self.job)
        self.assertEqual(task.id_serie, self.serie)

class CollectionViewsTestCase(TestCase):
    """Tests pour les vues de collection"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        
        # Créer des données de test
        publisher = Publisher.objects.create(title="Test Publisher")
        genre = Genre.objects.create(title="Test Genre")
        
        self.serie = Serie.objects.create(
            title="Test Serie",
            publisher=publisher,
            genre=genre
        )
        
        self.volume1 = Volume.objects.create(
            title="Volume 1",
            number=1,
            serie=self.serie
        )
        
        self.volume2 = Volume.objects.create(
            title="Volume 2",
            number=2,
            serie=self.serie
        )
        
        # Créer des possessions
        Possession.objects.create(user=self.user, volume=self.volume1)
        Possession.objects.create(user=self.user, volume=self.volume2)
    
    def test_collection_view_requires_login(self):
        """Test que la vue collection nécessite une connexion"""
        response = self.client.get('/collection/collection/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
    
    def test_collection_view_authenticated(self):
        """Test de la vue collection pour un utilisateur connecté"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/collection/collection/')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'collection.html')
        
        # Vérifier le contexte
        self.assertIn('series_with_volumes', response.context)
        self.assertIn('total_books', response.context)
        self.assertIn('total_series', response.context)
        
        # Vérifier les statistiques
        self.assertEqual(response.context['total_books'], 2)
        self.assertEqual(response.context['total_series'], 1)
        
        # Vérifier les séries avec volumes
        series_with_volumes = response.context['series_with_volumes']
        self.assertIn(self.serie, series_with_volumes)
        self.assertEqual(len(series_with_volumes), 2)
    
    def test_search_view_get_empty(self):
        """Test de la vue de recherche sans terme"""
        response = self.client.get('/collection/search/')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'search.html')
        
        # Vérifier le contexte
        self.assertEqual(response.context['series'], [])
        self.assertEqual(response.context['search_term'], "")
    
    def test_search_view_with_term(self):
        """Test de la vue de recherche avec terme de recherche"""
        response = self.client.get('/collection/search/', {'search': 'Test'})
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier le contexte
        series = list(response.context['series'])
        self.assertIn(self.serie, series)
        self.assertEqual(response.context['search_term'], 'Test')
    
    def test_search_view_no_results(self):
        """Test de la vue de recherche sans résultats"""
        response = self.client.get('/collection/search/', {'search': 'NonExistent'})
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier qu'il n'y a pas de résultats
        series = list(response.context['series'])
        self.assertEqual(len(series), 0)
    
    def test_serie_detail_view(self):
        """Test de la vue de détail d'une série"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/collection/serie/{self.serie.id}')
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier le contexte
        self.assertEqual(response.context['serie'], self.serie)
        self.assertEqual(response.context['total_volumes'], 2)
        self.assertEqual(response.context['possessed_volumes'], 2)
        self.assertEqual(response.context['completion_percentage'], 100.0)
        
        # Vérifier les volumes
        volumes = list(response.context['volumes'])
        self.assertEqual(len(volumes), 2)
        
        # Vérifier que les volumes sont marqués comme possédés
        for volume in volumes:
            self.assertTrue(volume.possessed)
    
    def test_serie_detail_view_nonexistent(self):
        """Test de la vue de détail pour une série inexistante"""
        self.client.login(username='testuser', password='testpass123')
        fake_id = uuid.uuid4()
        response = self.client.get(f'/collection/serie/{fake_id}')
        
        self.assertEqual(response.status_code, 404)

class CollectionIntegrationTestCase(TestCase):
    """Tests d'intégration pour le module collection"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        
        # Créer des données complètes
        self.author = Authors.objects.create(name="Oda", first_name="Eiichiro")
        self.publisher = Publisher.objects.create(title="Shogakukan")
        self.genre = Genre.objects.create(title="Adventure")
        self.kind = Kind.objects.create(title="Manga")
        
        self.serie = Serie.objects.create(
            title="One Piece",
            publisher=self.publisher,
            genre=self.genre
        )
        self.serie.kinds.add(self.kind)
        
        # Créer plusieurs volumes
        for i in range(1, 6):
            Volume.objects.create(
                title=f"Volume {i}",
                number=i,
                serie=self.serie
            )
        
        # L'utilisateur ne possède que les volumes 1, 3 et 5
        volumes_to_own = [1, 3, 5]
        for num in volumes_to_own:
            volume = Volume.objects.get(serie=self.serie, number=num)
            Possession.objects.create(user=self.user, volume=volume)
        
        # Créer des préférences
        like_genre.objects.create(user=self.user, genre=self.genre, like=True)
        like_kind.objects.create(user=self.user, kind=self.kind, like=True)
    
    def test_complete_collection_workflow(self):
        """Test du workflow complet de collection"""
        self.client.login(username='testuser', password='testpass123')
        
        # 1. Tester la vue collection
        response = self.client.get('/collection/collection/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_books'], 3)
        self.assertEqual(response.context['total_series'], 1)
        
        # 2. Tester la recherche
        response = self.client.get('/collection/search/', {'search': 'One Piece'})
        self.assertEqual(response.status_code, 200)
        series = list(response.context['series'])
        self.assertEqual(len(series), 1)
        self.assertEqual(series[0].title, "One Piece")
        
        # 3. Tester les détails de série
        response = self.client.get(f'/collection/serie/{self.serie.id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_volumes'], 5)
        self.assertEqual(response.context['possessed_volumes'], 3)
        self.assertEqual(response.context['completion_percentage'], 60.0)
        
        # Vérifier les volumes possédés/non possédés
        volumes = list(response.context['volumes'])
        possessed_numbers = [v.number for v in volumes if v.possessed]
        self.assertEqual(set(possessed_numbers), {1, 3, 5})
    
    def test_user_preferences_integration(self):
        """Test d'intégration des préférences utilisateur"""
        # Vérifier les préférences de genre
        user_genre_likes = like_genre.objects.filter(user=self.user)
        self.assertEqual(user_genre_likes.count(), 1)
        self.assertTrue(user_genre_likes.first().like)
        
        # Vérifier les préférences de kind
        user_kind_likes = like_kind.objects.filter(user=self.user)
        self.assertEqual(user_kind_likes.count(), 1)
        self.assertTrue(user_kind_likes.first().like)
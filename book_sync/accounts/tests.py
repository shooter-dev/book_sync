from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.messages import get_messages
from collection.models import like_kind, like_genre, Kind, Genre
import json

User = get_user_model()

class AuthenticationTestCase(TestCase):
    """Tests pour les vues d'authentification"""
    
    def setUp(self):
        self.client = Client()
        self.user_group = Group.objects.create(name='user')
        self.premium_group = Group.objects.create(name='premium')
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            age=25
        )
        self.user.groups.add(self.user_group)
    
    def test_login_view_get(self):
        """Test de l'affichage du formulaire de connexion"""
        response = self.client.get('/accounts/login/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'login.html')
        self.assertIn('form', response.context)
    
    def test_login_view_redirect_authenticated_user(self):
        """Test de redirection si l'utilisateur est déjà connecté"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/accounts/login/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/home/')
    
    def test_login_view_post_success(self):
        """Test de connexion réussie"""
        response = self.client.post('/accounts/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/home/')
        
        # Vérifier que l'utilisateur est connecté
        self.assertTrue(self.client.session.get('_auth_user_id'))
    
    def test_login_view_post_invalid_credentials(self):
        """Test de connexion avec identifiants invalides"""
        response = self.client.post('/accounts/login/', {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        
        # Vérifier les messages d'erreur
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('incorrect' in str(m) for m in messages))
    
    def test_login_view_remember_me(self):
        """Test de la fonction "Se souvenir de moi" """
        response = self.client.post('/accounts/login/', {
            'username': 'testuser',
            'password': 'testpass123',
            'remember-me': 'on'
        })
        self.assertEqual(response.status_code, 302)
        
        # Vérifier que la session a une durée de vie longue
        self.assertEqual(self.client.session.get_expiry_age(), 1209600)  # 2 semaines
    
    def test_login_view_without_remember_me(self):
        """Test de connexion sans "Se souvenir de moi" """
        response = self.client.post('/accounts/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)
        
        # Vérifier que la session expire à la fermeture du navigateur
        self.assertEqual(self.client.session.get_expiry_age(), 0)
    
    def test_logout_view(self):
        """Test de déconnexion"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/accounts/logout/')
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/home/')
        
        # Vérifier que l'utilisateur est déconnecté
        self.assertIsNone(self.client.session.get('_auth_user_id'))

class RegistrationTestCase(TestCase):
    """Tests pour l'inscription"""
    
    def setUp(self):
        self.client = Client()
        self.user_group = Group.objects.create(name='user')
    
    def test_register_view_get(self):
        """Test de l'affichage du formulaire d'inscription"""
        response = self.client.get('/accounts/register/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'register.html')
    
    def test_register_view_post_success(self):
        """Test d'inscription réussie"""
        response = self.client.post('/accounts/register/', {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'newpass123',
            'password2': 'newpass123'
        })
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))
        
        # Vérifier que l'utilisateur a été créé
        user = User.objects.get(username='newuser')
        self.assertEqual(user.email, 'newuser@example.com')
        
        # Vérifier que l'utilisateur a été ajouté au groupe 'user'
        self.assertTrue(user.groups.filter(name='user').exists())
        
        # Vérifier les messages de succès
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('créé avec succès' in str(m) for m in messages))
    
    def test_register_view_password_mismatch(self):
        """Test d'inscription avec mots de passe différents"""
        response = self.client.post('/accounts/register/', {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'newpass123',
            'password2': 'differentpass'
        })
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier les messages d'erreur
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('ne correspondent pas' in str(m) for m in messages))
        
        # Vérifier que l'utilisateur n'a pas été créé
        self.assertFalse(User.objects.filter(username='newuser').exists())
    
    def test_register_view_existing_username(self):
        """Test d'inscription avec un nom d'utilisateur existant"""
        User.objects.create_user(username='existinguser', password='pass123')
        
        response = self.client.post('/accounts/register/', {
            'username': 'existinguser',
            'email': 'new@example.com',
            'password1': 'newpass123',
            'password2': 'newpass123'
        })
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier les messages d'erreur
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('déjà pris' in str(m) for m in messages))
    
    def test_register_view_missing_fields(self):
        """Test d'inscription avec champs manquants"""
        response = self.client.post('/accounts/register/', {
            'username': 'newuser',
            'email': '',
            'password1': 'newpass123',
            'password2': 'newpass123'
        })
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier les messages d'erreur
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('obligatoires' in str(m) for m in messages))

class ProfileTestCase(TestCase):
    """Tests pour le profil utilisateur"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            age=25
        )
        
        # Créer des données de test
        self.genre = Genre.objects.create(title='Action')
        self.kind = Kind.objects.create(title='Manga')
        
        # Créer des préférences
        like_genre.objects.create(user=self.user, genre=self.genre, like=True)
        like_kind.objects.create(user=self.user, kind=self.kind, like=False)
    
    def test_profile_view_authenticated(self):
        """Test de la vue profil pour un utilisateur connecté"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/accounts/profile/')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'profile.html')
        self.assertIn('kinds_data', response.context)
        self.assertIn('genres_data', response.context)
        
        # Vérifier les données JSON
        kinds_data = json.loads(response.context['kinds_data'}/'
        genres_data = json.loads(response.context['genres_data'}/'
        
        self.assertEqual(len(kinds_data), 1)
        self.assertEqual(len(genres_data), 1)
        self.assertEqual(kinds_data[0]['title'], 'Manga')
        self.assertEqual(genres_data[0]['title'], 'Action')
    
    def test_profile_view_unauthenticated(self):
        """Test de la vue profil pour un utilisateur non connecté"""
        response = self.client.get('/accounts/profile/')
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('kinds_data', response.context)
        self.assertNotIn('genres_data', response.context)

class SubscriptionTestCase(TestCase):
    """Tests pour les abonnements premium"""
    
    def setUp(self):
        self.client = Client()
        self.user_group = Group.objects.create(name='user')
        self.premium_group = Group.objects.create(name='premium')
        
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.user.groups.add(self.user_group)
    
    def test_subscribe_view_get(self):
        """Test de l'affichage de la page d'abonnement"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/accounts/subscribe/')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'subscribe.html')
    
    def test_subscribe_view_post_success(self):
        """Test d'abonnement premium réussi"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post('/accounts/subscribe/')
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/home/')
        
        # Vérifier que l'utilisateur est maintenant premium
        self.user.refresh_from_db()
        self.assertTrue(self.user.groups.filter(name='premium').exists())
        self.assertFalse(self.user.groups.filter(name='user').exists())
        
        # Vérifier les messages de succès
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('premium' in str(m) for m in messages))
    
    def test_subscribe_view_requires_login(self):
        """Test que l'abonnement nécessite une connexion"""
        response = self.client.get('/accounts/subscribe/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/register/', response.url)
    
    def test_cancel_subscription(self):
        """Test d'annulation d'abonnement premium"""
        self.user.groups.clear()
        self.user.groups.add(self.premium_group)
        
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post('/accounts/cancel-subscription/')
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))
        
        # Vérifier que l'utilisateur n'est plus premium
        self.user.refresh_from_db()
        self.assertFalse(self.user.groups.filter(name='premium').exists())

class PasswordChangeTestCase(TestCase):
    """Tests pour le changement de mot de passe"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='oldpass123'
        )
    
    def test_change_password_success(self):
        """Test de changement de mot de passe réussi"""
        self.client.login(username='testuser', password='oldpass123')
        
        response = self.client.post('/accounts/changer-mdp/', {
            'old_password': 'oldpass123',
            'new_password1': 'newpass123',
            'new_password2': 'newpass123'
        })
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))
        
        # Vérifier que le mot de passe a été changé
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpass123'))
        
        # Vérifier les messages de succès
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('changé avec succès' in str(m) for m in messages))
    
    def test_change_password_wrong_old_password(self):
        """Test de changement de mot de passe avec ancien mot de passe incorrect"""
        self.client.login(username='testuser', password='oldpass123')
        
        response = self.client.post('/accounts/changer-mdp/', {
            'old_password': 'wrongpass',
            'new_password1': 'newpass123',
            'new_password2': 'newpass123'
        })
        
        self.assertEqual(response.status_code, 302)
        
        # Vérifier que le mot de passe n'a pas été changé
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('oldpass123'))
        
        # Vérifier les messages d'erreur
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('incorrect' in str(m) for m in messages))
    
    def test_change_password_mismatch(self):
        """Test de changement de mot de passe avec nouveaux mots de passe différents"""
        self.client.login(username='testuser', password='oldpass123')
        
        response = self.client.post('/accounts/changer-mdp/', {
            'old_password': 'oldpass123',
            'new_password1': 'newpass123',
            'new_password2': 'differentpass'
        })
        
        self.assertEqual(response.status_code, 302)
        
        # Vérifier que le mot de passe n'a pas été changé
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('oldpass123'))
        
        # Vérifier les messages d'erreur
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('ne correspondent pas' in str(m) for m in messages))

class AgeManagementTestCase(TestCase):
    """Tests pour la gestion de l'âge"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_update_age_info_success(self):
        """Test de mise à jour d'âge réussie"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post('/accounts/update-age-info/', {
            'age': '25'
        })
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/profile/')
        
        # Vérifier que l'âge a été sauvegardé
        self.user.refresh_from_db()
        self.assertEqual(self.user.age, 25)
        self.assertTrue(self.user.is_adult)
        
        # Vérifier les messages
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('sauvegardées' in str(m) for m in messages))
    
    def test_update_age_info_minor(self):
        """Test de mise à jour d'âge pour un mineur"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post('/accounts/update-age-info/', {
            'age': '15'
        })
        
        self.assertEqual(response.status_code, 302)
        
        # Vérifier les paramètres pour mineur
        self.user.refresh_from_db()
        self.assertEqual(self.user.age, 15)
        self.assertFalse(self.user.is_adult)
        self.assertFalse(self.user.show_mature_content)
    
    def test_update_age_info_already_set(self):
        """Test de tentative de modification d'âge déjà défini"""
        self.user.age = 20
        self.user.save()
        
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post('/accounts/update-age-info/', {
            'age': '25'
        })
        
        self.assertEqual(response.status_code, 302)
        
        # Vérifier que l'âge n'a pas changé
        self.user.refresh_from_db()
        self.assertEqual(self.user.age, 20)
        
        # Vérifier les messages d'erreur
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('déjà défini' in str(m) for m in messages))
    
    def test_update_age_info_invalid_age(self):
        """Test de mise à jour avec âge invalide"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post('/accounts/update-age-info/', {
            'age': '150'
        })
        
        self.assertEqual(response.status_code, 302)
        
        # Vérifier que l'âge n'a pas été défini
        self.user.refresh_from_db()
        self.assertIsNone(self.user.age)
        
        # Vérifier les messages d'erreur
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('compris entre' in str(m) for m in messages))

class MatureContentTestCase(TestCase):
    """Tests pour la gestion du contenu mature"""
    
    def setUp(self):
        self.client = Client()
        self.adult_user = User.objects.create_user(
            username='adult',
            password='testpass123',
            age=20,
            is_adult=True
        )
        
        self.minor_user = User.objects.create_user(
            username='minor',
            password='testpass123',
            age=15,
            is_adult=False
        )
    
    def test_update_mature_content_adult_success(self):
        """Test de mise à jour du contenu mature pour un adulte"""
        self.client.login(username='adult', password='testpass123')
        
        response = self.client.post('/accounts/update-mature-content/', {
            'show_mature_content': '1'
        })
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/profile/')
        
        # Vérifier que le paramètre a été mis à jour
        self.adult_user.refresh_from_db()
        self.assertTrue(self.adult_user.show_mature_content)
    
    def test_update_mature_content_minor_denied(self):
        """Test de refus de modification pour un mineur"""
        self.client.login(username='minor', password='testpass123')
        
        response = self.client.post('/accounts/update-mature-content/', {
            'show_mature_content': '1'
        })
        
        self.assertEqual(response.status_code, 302)
        
        # Vérifier les messages d'erreur
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('16 ans ou plus' in str(m) for m in messages))

class UserDeletionTestCase(TestCase):
    """Tests pour la suppression d'utilisateur"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.user_to_delete = User.objects.create_user(
            username='usertodelete',
            password='testpass123'
        )
    
    def test_delete_user_success(self):
        """Test de suppression d'utilisateur réussie"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(f'/accounts/delete_user/{self.user_to_delete.pk}/')
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/home/')
        
        # Vérifier que l'utilisateur a été supprimé
        self.assertFalse(User.objects.filter(pk=self.user_to_delete.pk).exists())
        
        # Vérifier les messages
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('supprimé' in str(m) for m in messages))
    
    def test_delete_user_nonexistent(self):
        """Test de suppression d'utilisateur inexistant"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(f'/accounts/delete_user/{99999}/')
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/home/')
        
        # Vérifier les messages d'erreur
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("n'a pas pu être" in str(m) for m in messages))
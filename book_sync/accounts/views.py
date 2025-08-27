from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.views.decorators.cache import never_cache
from .models import CustomUser as User
from django.contrib.auth.models import Group
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from collection.models import like_kind, like_genre
import json
from django.views.decorators.http import require_POST

@never_cache
@csrf_protect
def login_view(request):
    """
    Vue de login
    Gère l'authentification des utilisateurs
    """
    if request.user.is_authenticated:
        return redirect('index')  # Rediriger si déjà connecté

    form = AuthenticationForm()

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            remember_me = request.POST.get('remember-me')

            user = authenticate(username=username, password=password)

            if user is not None:
                auth_login(request, user)

                # Gestion du "Se souvenir de moi"
                if not remember_me:
                    request.session.set_expiry(0)  # Expire à la fermeture du navigateur
                else:
                    request.session.set_expiry(1209600)  # 2 semaines

                messages.success(request, f'Bienvenue {user.username} !')

                # Redirection après connexion
                next_url = request.GET.get('next', 'index')
                return redirect(next_url)
            else:
                messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')

    context = {
        'form': form,
        'title': 'Connexion - BookSync'
    }

    return render(request, 'login.html', context)

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        email = request.POST.get('email')

        if not username or not password1 or not password2 or not email:
            messages.error(request, "Tous les champs sont obligatoires.")
            print("Champs manquants.")
        elif password1 != password2:
            messages.error(request, "Les mots de passe ne correspondent pas.")
            print("Les mots de passe ne correspondent pas.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Ce nom d'utilisateur est déjà pris.")
            print("nom déja pris")
        else:
            user = User.objects.create_user(username=username, password=password1, email=email)
            # Assigner automatiquement le nouveau utilisateur au groupe 'user'
            #user_group, created = Group.objects.get_or_create(name='user')
            user_group = Group.objects.get(name='user')
            print(
                f"User Group : {user_group}"
            )
            user.groups.add(user_group)
            print(f" USER GROUPS : {user_group}")
            print(username, password1, email)
            messages.success(request, "Votre compte a été créé avec succès. Vous pouvez vous connecter.")
            print("Votre compte a été créé avec succès. Vous pouvez vous connecter.")
            return redirect('login')

    return render(request, 'register.html')

def logout_view(request):
    logout(request)
    request.session.flush()

    storage = messages.get_messages(request)
    storage.used = True

    messages.info(request, "Vous êtes maintenant déconnecté.")
    return redirect('index')

def profile_view(request):
    # Récupérer les kinds et genres avec les préférences de l'utilisateur
    context = {}
    
    if request.user.is_authenticated:
        # Récupérer SEULEMENT les préférences existantes de l'utilisateur
        user_kind_likes = like_kind.objects.filter(user=request.user).select_related('kind')
        user_genre_likes = like_genre.objects.filter(user=request.user).select_related('genre')
        
        # Préparer les données pour le template - seulement les préférences existantes
        kinds_data = []
        for like in user_kind_likes:
            kinds_data.append({
                'id': str(like.kind.id),
                'title': like.kind.title,
                'userPreference': like.like
            })
            
        genres_data = []
        for like in user_genre_likes:
            genres_data.append({
                'id': str(like.genre.id),
                'title': like.genre.title,
                'userPreference': like.like
            })
        
        context['kinds_data'] = json.dumps(kinds_data)
        context['genres_data'] = json.dumps(genres_data)
    
    return render(request, 'profile.html', context)

@login_required(login_url='register')
def subscribe(request):
    if request.method == 'POST':
        user = request.user
        
        # Ajouter l'utilisateur au groupe premium
        premium_group, created = Group.objects.get_or_create(name='premium')
        user_group = Group.objects.get(name='user')
        
        # Retirer du groupe user et ajouter au groupe premium
        user.groups.remove(user_group)
        user.groups.add(premium_group)
        
        messages.success(request, 'Félicitations ! Vous êtes maintenant un utilisateur premium.')
        return redirect('index')  # Rediriger vers la page d'accueil
    
    return render(request, 'subscribe.html')

@login_required
def change_password_view(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')

        if not request.user.check_password(old_password):
            messages.error(request, 'Le mot de passe actuel est incorrect.')
            return redirect('login')

        if new_password1 != new_password2:
            messages.error(request, 'Les nouveaux mots de passe ne correspondent pas.')
            return redirect('login')

        form = PasswordChangeForm(request.user, {
            'old_password': old_password,
            'new_password1': new_password1,
            'new_password2': new_password2
        })

        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, 'Votre mot de passe a été changé avec succès.')
            return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Erreur: {error}')
            return redirect('login')

    return redirect('index')

@login_required(login_url='login')
@csrf_exempt
def delete_user(request,pk):
            try:
                user= User.objects.get(pk=pk)
                user.delete()
                messages.info(request, "Utilisateur supprimé")
                return redirect('index')
            except Exception as e:
                messages.info(request, "Erreur, Utilisateur n'a pas pu être supprimer supprimé")
                return redirect('index')

@login_required
def update_age_info(request):
    """
    Vue pour mettre à jour les informations d'âge de l'utilisateur
    IMPORTANT: L'âge ne peut être défini qu'une seule fois pour des raisons de sécurité
    """
    if request.method == 'POST':
        user = request.user
        
        if user.age is not None:
            messages.error(request, 'Votre âge est déjà défini et ne peut pas être modifié pour des raisons de sécurité.')
            return redirect('profile')
        
        age = request.POST.get('age')
        if age:
            try:
                age = int(age)
                if 1 <= age <= 120:
                    user.age = age
                else:
                    messages.error(request, 'L\'âge doit être compris entre 1 et 120 ans.')
                    return redirect('profile')
            except ValueError:
                messages.error(request, 'Veuillez entrer un âge valide.')
                return redirect('profile')
        else:
            messages.error(request, 'Veuillez saisir votre âge.')
            return redirect('profile')
        
        is_adult = age >= 18
        user.is_adult = is_adult
        
        if age < 16:
            user.show_mature_content = False
        
        user.save()
        
        if is_adult:
            messages.success(request, 'Vos informations d\'âge ont été définitivement sauvegardées. Vous pouvez maintenant accéder aux paramètres de contenu mature.')
        else:
            messages.success(request, 'Vos informations d\'âge ont été définitivement sauvegardées.')
        
        messages.info(request, '⚠️ Important: Ces informations ne peuvent plus être modifiées.')
        
        return redirect('profile')
    
    return redirect('profile')

@login_required
def update_mature_content(request):
    """
    Vue pour mettre à jour les préférences d'affichage du contenu mature
    """
    if request.method == 'POST':
        user = request.user
        
        if not user.can_access_mature_content:
            messages.error(request, 'Vous devez être âgé de 16 ans ou plus pour modifier ces paramètres.')
            return redirect('profile')
        
        show_mature = request.POST.get('show_mature_content') == '1'
        user.show_mature_content = show_mature
        user.save()
        
        if show_mature:
            messages.success(request, 'Les couvertures explicites seront désormais affichées.')
        else:
            messages.success(request, 'Les couvertures explicites seront désormais masquées.')
        
        return redirect('profile')
    
    return redirect('profile')

@require_POST
@login_required
def cancel_subscription(request):
    if request.method == 'POST':
        user = request.user
        user_group, created = Group.objects.get_or_create(name='premium')
        user.groups.remove(user_group)
        print(f" USER GROUPS : {user_group}")

        return redirect('login')

    return redirect('/accounts/profile')



from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.views.decorators.cache import never_cache
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages


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
        print(username, password1, password2, email)
        print(request.POST)

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
            User.objects.create_user(username=username, password=password1, email=email)
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
    return render(request, 'profile.html')

@login_required(login_url='register')
def subscribe(request):
    return render(request, 'subscribe.html')

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
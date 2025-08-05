from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django.urls import reverse


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
    return render(request, 'register.html')
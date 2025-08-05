from django.contrib.auth import logout
from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import render, redirect

# Create your views here.
def register_view(request):
    return render(request, 'register.html')


def logout_view(request):
    logout(request)
    request.session.flush()

    storage = messages.get_messages(request)
    storage.used = True

    messages.info(request, "Vous êtes maintenant déconnecté.")
    return redirect('index')
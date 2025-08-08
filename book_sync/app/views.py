from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'index.html')


def collection(request):
    return render(request, 'collection.html')

def recommendation(request):
    return render(request, 'recommendation.html')
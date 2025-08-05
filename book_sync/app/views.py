from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'index.html')

def research(request):
    return render(request, 'research.html')

def collection(request):
    return render(request, 'collection.html')


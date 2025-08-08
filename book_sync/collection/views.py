from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Possession, Volume, Serie, Genre, Publisher


@login_required
def collection(request):
    # Récupérer les possessions de l'utilisateur
    possessions = Possession.objects.filter(user=request.user).select_related('volume__serie__genre', 'volume__serie__publisher')
    
    # Grouper par série
    series_with_volumes = {}
    for possession in possessions:
        serie = possession.volume.serie
        if serie not in series_with_volumes:
            series_with_volumes[serie] = []
        series_with_volumes[serie].append(possession)
    
    # Trier les volumes par numéro dans chaque série
    for serie, volumes in series_with_volumes.items():
        volumes.sort(key=lambda x: x.volume.number)
    
    # Statistiques
    total_books = possessions.count()
    total_series = len(series_with_volumes)
    
    context = {
        'series_with_volumes': series_with_volumes,
        'total_books': total_books,
        'total_series': total_series,
        'lus': 0,  # À implémenter plus tard
        'en_cours': 0,  # À implémenter plus tard
        'favoris': 0,  # À implémenter plus tard
    }
    
    return render(request, 'collection.html', context)
  
@csrf_exempt
def search(request):
    series = []
    search_term = ""

    if request.method == "GET" and request.GET.get('search'):
        search_term = request.GET.get('search')
        series = Serie.objects.filter(title__icontains=search_term)#.select_related('genre', 'publisher')

    context = {
        'series': series,
        'search_term': search_term,
    }
    return render(request, 'search.html', context)

# class ResultPageView(TemplateView):
#     template_name = 'result.html'

# class SearchResultsView(ListView):
#     model = Serie
#     template_name = "result_research.html"
#
#     def get_queryset(request,self):
#         if request.method == "POST":
#             search = request.POST["search"]
#             print("****************************************************")
#             print(Serie.objects.filter(title__icontains=search))
#             object_list =Serie.objects.filter(title__icontains=search)
#           return object_list

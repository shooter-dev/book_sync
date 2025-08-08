#from ftplib import print_line

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, TemplateView
from collection.models import Serie
# Create your views here.

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
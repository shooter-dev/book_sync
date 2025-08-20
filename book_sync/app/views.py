import os

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
import requests
from django.http import JsonResponse
from dotenv import load_dotenv

load_dotenv()

def index(request):
    return render(request, 'index.html')


def collection(request):
    return render(request, 'collection.html')

def recommendation(request):
    return render(request, 'recommendation.html')

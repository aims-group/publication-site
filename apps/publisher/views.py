from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader, Context
from django.contrib.auth.decorators import login_required

def index(request):
    return render(request, 'site/search.html')

def register(request):
  return HttpResponse("Register page")

def login(request):
  return HttpResponse("login page")

from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader, Context

def index(request):
    return render(request, 'base.html')

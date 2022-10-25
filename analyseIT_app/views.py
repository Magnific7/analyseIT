import re
from django.shortcuts import render, HttpResponse ,HttpResponseRedirect, redirect


def Index(request):
    return render(request, 'index.html', {})

def History_page(request):
    return render(request, 'history.html', {})

def Login(request):
    return render(request, 'login.html', {})

def Cancel(request):
    return render(request, 'index.html')

def Charts(request):
    
    return render(request, 'charts.html', {})

from django.shortcuts import render

def index(request):
  context = {}
  return render(request, 'public/index.html', context)

def htmlreference(request):
  context = {}
  return render(request, 'common/reference.html', context)
from django.shortcuts import render

def producers_index(request):
  context = {}
  return render(request, 'producers/index.html', context)


from django.shortcuts import render

def administrators_index(request):
  context = {}
  return render(request, 'administrators/index.html', context)


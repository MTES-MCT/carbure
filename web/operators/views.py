from django.shortcuts import render

def operators_index(request):
  context = {}
  return render(request, 'operators/index.html', context)


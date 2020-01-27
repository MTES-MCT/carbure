from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def producers_index(request):
  context = {}
  return render(request, 'producers/index.html', context)


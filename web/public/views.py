from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404

from core.models import UserRights

def index(request):
  context = {}
  if request.user.is_authenticated:
    return redirect('home')
  return render(request, 'public/index.html', context)

@login_required
def home(request):
  try:
    rights = UserRights.objects.filter(user=request.user)
    default_entity = rights[0] 
  except:
    # todo: raise an error? add notification to administrator?
    return render(request, 'public/blank_user.html', {})

  if default_entity.entity.entity_type == 'Administrateur':
    return redirect('administrators-index')
  elif default_entity.entity.entity_type == 'Producteur':
    return redirect('producers-index')
  elif default_entity.entity.entity_type == 'Opérateur':
    return redirect('operators-index')
  else:
    raise Http404("Unknown User Type")

@login_required
def annuaire(request):
  context = {}
  return render(request, 'public/annuaire.html', context)

def htmlreference(request):
  context = {}
  return render(request, 'common/reference.html', context)
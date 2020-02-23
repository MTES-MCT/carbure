from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404

from core.models import UserRights, UserPreferences
from core.decorators import enrich_with_user_details

def index(request):
  context = {}
  if request.user.is_authenticated:
    return redirect('home')
  return render(request, 'public/index.html', context)

@login_required
@enrich_with_user_details
def home(request, *args, **kwargs):
  context = kwargs['context']
  if context['user_entity'].entity_type == 'Administration':
    return redirect('administrators-index')
  elif context['user_entity'].entity_type == 'Producteur':
    return redirect('producers-index')
  elif context['user_entity'].entity_type == 'Opérateur':
    return redirect('operators-index')
  else:
    raise Http404("Unknown User Type")

def htmlreference(request):
  context = {}
  return render(request, 'common/reference.html', context)

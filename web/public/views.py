from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404

from core.models import PlatformUser

def index(request):
  context = {}
  return render(request, 'public/index.html', context)

@login_required
def home(request):
  try:
    user = PlatformUser.objects.get(user=request.user)
  except:
    # todo: raise an error? add notification to administrator?
    return render(request, 'public/blank_user.html', {})

  if user.user_type == 'Administrateur':
    return redirect('administrators-index')
  elif user.user_type == 'Producteur':
    return redirect('producers-index')
  elif user.user_type == 'Opérateur':
    return redirect('operators-index')
  else:
    raise Http404("Unknown User Type")

def htmlreference(request):
  context = {}
  return render(request, 'common/reference.html', context)
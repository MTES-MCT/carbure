from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def producers_index(request):
  context = {}
  context['current_url_name'] = 'producers-index'
  return render(request, 'producers/attestations.html', context)

@login_required
def producers_inbox(request):
  context = {}
  context['current_url_name'] = 'producers-inbox'
  return render(request, 'producers/inbox.html', context)

@login_required
def producers_settings(request):
  context = {}
  context['current_url_name'] = 'producers-settings'
  return render(request, 'producers/settings.html', context)

@login_required
def producers_attestation(request):
  context = {}
  context['current_url_name'] = 'producers-attestation'
  return render(request, 'producers/attestation.html', context)


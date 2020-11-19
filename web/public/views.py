from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404

from core.decorators import enrich_with_user_details


def index(request):
    context = {}
    if request.user.is_authenticated:
        return redirect('/v2/')
    return render(request, 'public/index.html', context)


def stats(request):
    return redirect('https://metabase.carbure.beta.gouv.fr/public/dashboard/a9c045a5-c2fb-481a-ab85-f55bce8ae3c0')


def annuaire(request):
    context = {}
    return render(request, 'public/index.html', context)

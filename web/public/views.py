from django.shortcuts import render
from django.shortcuts import redirect


def index(request):
    context = {}
    if request.user.is_verified:
        return redirect('/v2/')
    return render(request, 'public/index.html', context)


def stats(request):
    return redirect('https://metabase.carbure.beta.gouv.fr/public/dashboard/a9c045a5-c2fb-481a-ab85-f55bce8ae3c0')


def annuaire(request):
    context = {}
    return render(request, 'public/index.html', context)

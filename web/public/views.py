from django.shortcuts import render
from django.shortcuts import redirect


def index(request):
    return redirect('/app/')


def stats(request):
    return redirect('https://metabase.carbure.beta.gouv.fr/public/dashboard/d2da144c-9674-41bd-83e5-4bc9cbb98b50')


def annuaire(request):
    context = {}
    return render(request, 'public/index.html', context)

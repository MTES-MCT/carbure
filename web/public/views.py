from django.shortcuts import redirect

def index(request):
    return redirect('/app/')

def stats(request):
    return redirect('/app/stats')
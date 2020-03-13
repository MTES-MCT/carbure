from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from core.decorators import enrich_with_user_details

@login_required
@enrich_with_user_details
def profile(request, *args, **kwargs):
    context = kwargs['context']
    return render(request, "accounts/profile.html", context)


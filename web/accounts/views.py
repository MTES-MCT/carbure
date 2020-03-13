from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

@login_required
def profile(request):
    return render(request, "accounts/profile.html")


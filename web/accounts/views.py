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

@login_required
@enrich_with_user_details
def custom_password_change(request, *args, **kwargs):
    context = kwargs['context']
    if request.method == 'POST':
        request.user.set_password(request.POST['new_password1'])
        request.user.save()
        redirect('custom_password_change_success')
    return render(request, "accounts/password_change.html", context)

@login_required
@enrich_with_user_details
def custom_password_change_success(request, *args, **kwargs):
    context = kwargs['context']
    return render(request, "accounts/password_change_done.html", context)


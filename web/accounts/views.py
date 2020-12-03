from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from core.decorators import enrich_with_user_details
from django.contrib.auth import get_user_model


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


def register(request):
    name = request.POST.get('name', False)
    email = request.POST.get('email', False)

    errors = []
    if request.method == 'POST':
        if not name:
            errors.append('Veuillez spécifier votre nom')
        if not email:
            errors.append('Veuillez spécifier votre adresse email')
        if errors:
            return render(request, "registration/register.html", {'errors': errors, 'email': email if email else '', 'name': name if name else ''})
        user_model = get_user_model()
        try:
            obj, created = user_model.objects.update_or_create(name=name, email=email)
        except:
            return render(request, "registration/register.html", {'errors': ['Utilisateur déjà inscrit'], 'email': email if email else '', 'name': name if name else ''})
        return render(request, "registration/register_complete.html")
    return render(request, "registration/register.html")
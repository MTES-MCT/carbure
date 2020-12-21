from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from core.decorators import enrich_with_user_details
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from authtools.forms import UserCreationForm
from accounts.tokens import account_activation_token
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text

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
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            subject = 'Carbure - Activation de compte'
            message = render_to_string('registration/account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            user.email_user(subject, message)
            return redirect('account_activation_sent')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


def account_activation_sent(request):
    return render(request, 'registration/account_activation_sent.html')


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.profile.email_confirmed = True
        user.save()
        login(request, user)
        return render(request, 'registration/account_activation_valid.html')
    else:
        return render(request, 'registration/account_activation_invalid.html')


def hotp_verify(request):
    pass


def resend_activation_link(request):
    pass

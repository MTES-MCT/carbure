import datetime
import pytz
# django
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.template import loader
from django.conf import settings
from django.utils import timezone

# plugins
from django_otp.plugins.otp_email.models import EmailDevice
from django_otp import user_has_device, devices_for_user
from django_otp import login as login_with_device
from authtools.forms import UserCreationForm
# app
from core.decorators import enrich_with_user_details
from accounts.tokens import account_activation_token
from accounts.forms import UserResendActivationLinkForm, OTPForm

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
        redirect('custom-password-change-success')
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
            # send email
            email_subject = 'Carbure - Activation de compte'
            email_context = {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            }
            html_message = loader.render_to_string('registration/account_activation_email.html', email_context)
            text_message = loader.render_to_string('registration/account_activation_email.txt', email_context)
            send_mail(
                subject=email_subject,
                message=text_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                html_message=html_message,
                recipient_list=[user.email],
                fail_silently=False,
            )
            email_otp = EmailDevice()
            email_otp.user = user
            email_otp.name = 'email'
            email_otp.confirmed = True
            email_otp.email = user.email
            email_otp.save()
            return redirect('account-activation-sent')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


def account_activation_sent(request):
    return render(request, 'registration/account_activation_sent.html')


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user_model = get_user_model()
        user = user_model.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return render(request, 'registration/account_activation_valid.html')
    else:
        return render(request, 'registration/account_activation_invalid.html')

# static - not an endpoint
def send_new_token(request):
    device = EmailDevice.objects.get(user=request.user)
    current_site = get_current_site(request)
    # if current token is expired, generate a new one
    now = timezone.now()
    if now > device.valid_until:
        device.generate_token()
    email_subject = 'Carbure - Code de Sécurité'
    email_context = {
        'user': request.user,
        'domain': current_site.domain,
        'token': device.token,
    }
    html_message = loader.render_to_string('accounts/otp_token_email.html', email_context)
    text_message = loader.render_to_string('accounts/otp_token_email.txt', email_context)
    send_mail(
        subject=email_subject,
        message=text_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        html_message=html_message,
        recipient_list=[request.user.email],
        fail_silently=False,
    )

@login_required
def otp_verify(request):
    # for old users that did not register when 2fa was introduced
    if not user_has_device(request.user):
        email_otp = EmailDevice()
        email_otp.user = request.user
        email_otp.name = 'email'
        email_otp.confirmed = True
        email_otp.email = request.user.email
        email_otp.save()

    if request.method == 'POST':
        form = OTPForm(request.user, request.POST)
        if form.is_valid():
            device = EmailDevice.objects.get(user=request.user)
            if device.verify_token(form.clean_otp_token()):
                login_with_device(request, device)
                return redirect('/v2')
            else:
                print('invalid token. expected %s got %s' % (device.token, form.clean_otp_token()))
                is_allowed, _ = device.verify_is_allowed()
                now = timezone.now()
                if now > device.valid_until:
                    form.add_error('otp_token', "Code Expiré. Un nouveau code vient d'être envoyé")
                    send_new_token(request)
                elif device.token != form.clean_otp_token():
                    dt = device.valid_until.astimezone(pytz.timezone('Europe/Paris'))
                    form.add_error('otp_token', "Code Invalide. Le dernier code envoyé est valide jusqu'à %s %s" % (dt.strftime('%H:%M'), dt.tzname()))
                elif not is_allowed:
                    delay_required = device.get_throttle_factor() * (2 ** (device.throttling_failure_count - 1))
                    form.add_error('otp_token', "Rate limited. Please try again in %d seconds" % (delay_required))
                else:
                    # unknown error
                    form.add_error('otp_token', "Erreur serveur")
                return render(request, 'accounts/otp_verify.html', {'form': form})
        else:
            print('form is invalid')
    else:
        # send token by email and display form
        send_new_token(request)
        form = OTPForm(request.user)
    return render(request, 'accounts/otp_verify.html', {'form': form})


def resend_activation_link(request):
    if request.method == 'POST':
        form = UserResendActivationLinkForm(request.POST)
        if form.is_valid():
            usermodel = get_user_model()
            try:
                user = usermodel.objects.get(email=form.clean_email())
                current_site = get_current_site(request)
                email_subject = 'Carbure - Activation de compte'
                email_context = {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': account_activation_token.make_token(user),
                }
                html_message = render_to_string('registration/account_activation_email.html', email_context)
                text_message = render_to_string('registration/account_activation_email.txt', email_context)
                send_mail(
                    subject=email_subject,
                    message=text_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    html_message=html_message,
                    recipient_list=[user.email],
                    fail_silently=False,
                )
                return render(request, 'registration/resend_activation_link_done.html', {'form': form})
            except Exception as e:
                print(e)
                return render(request, 'registration/resend_activation_link.html', {'form': form})
    else:
        form = UserResendActivationLinkForm()
    return render(request, 'registration/resend_activation_link.html', {'form': form})

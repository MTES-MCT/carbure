import pytz
from django.http.response import JsonResponse
from django.contrib.sites.shortcuts import get_current_site
from authtools.forms import UserCreationForm
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils import timezone
from accounts.tokens import account_activation_token
from django.template import loader
from django.conf import settings
from django_otp.plugins.otp_email.models import EmailDevice
from django.core.mail import send_mail
from django.contrib.auth import authenticate, logout
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth.decorators import login_required
from django_otp import user_has_device
from accounts.forms import UserResendActivationLinkForm, OTPForm
from django_otp import login as login_with_device
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.auth import login

def register(request):
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
        html_message = loader.render_to_string('emails/account_activation_email.html', email_context)
        text_message = loader.render_to_string('emails/account_activation_email.txt', email_context)
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
        return JsonResponse({'status': 'success', 'message': 'User Created'})
    else:
        errors = {key: e for key, e in form.errors.items()}
        return JsonResponse({'status': 'error', 'message': 'Invalid Form', 'errors': errors}, status=400)

def user_login(request):
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    user = authenticate(username=username, password=password)
    login(request, user)
    try:
        if user.is_authenticated:
            request.session.set_expiry(3 * 30 * 24 * 60 * 60) # 3 months
            return JsonResponse({'status': 'success', 'message': 'User logged in'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid credentials'}, status=400)
    except:
        return JsonResponse({'status': 'error', 'message': 'Account not activated'}, status=400)

def user_logout(request):
    logout(request)
    return JsonResponse({'status': 'success'})

@login_required
def request_otp(request):
    # send token by email and display form
    send_new_token(request)
    if not user_has_device(request.user):
        email_otp = EmailDevice()
        email_otp.user = request.user
        email_otp.name = 'email'
        email_otp.confirmed = True
        email_otp.email = request.user.email
        email_otp.save()
    device = EmailDevice.objects.get(user=request.user)
    dt = device.valid_until.astimezone(pytz.timezone('Europe/Paris'))
    return JsonResponse({'status': 'success', 'valid_until': dt.strftime("%m/%d/%Y, %H:%M")})

@login_required
def verify_otp(request):
    # for old users that did not register when 2fa was introduced
    if not user_has_device(request.user):
        email_otp = EmailDevice()
        email_otp.user = request.user
        email_otp.name = 'email'
        email_otp.confirmed = True
        email_otp.email = request.user.email
        email_otp.save()

    form = OTPForm(request.user, request.POST)
    if form.is_valid():
        device = EmailDevice.objects.get(user=request.user)
        if device.verify_token(form.clean_otp_token()):
            login_with_device(request, device)
            return JsonResponse({'status': 'success'})
        else:
            is_allowed, _ = device.verify_is_allowed()
            now = timezone.now()
            if now > device.valid_until:
                return JsonResponse({'status': 'error', 'message': 'Code expired'}, status=400)
            elif device.token != form.clean_otp_token():
                return JsonResponse({'status': 'error', 'message': 'Code invalid'}, status=400)
            elif not is_allowed:
                return JsonResponse({'status': 'error', 'message': 'Rate limited'}, status=400)
            else:
                return JsonResponse({'status': 'error', 'message': 'Unknown error'}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid Form'}, status=400)

def request_password_reset(request):
    username = request.POST.get('username', '')
    try:
        user = get_user_model().objects.get(email=username)
    except:
        return JsonResponse({'status': 'error', 'message': 'User not found'}, status=400)

    prtg = PasswordResetTokenGenerator()
    current_site = get_current_site(request)
    # send email
    email_subject = 'Carbure - Réinitialisation du mot de passe'
    email_context = {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': prtg.make_token(user),
    }
    html_message = loader.render_to_string('emails/password_reset_email.html', email_context)
    text_message = loader.render_to_string('emails/password_reset_email.txt', email_context)
    send_mail(
        subject=email_subject,
        message=text_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        html_message=html_message,
        recipient_list=[user.email],
        fail_silently=False,
    )
    return JsonResponse({'status': 'success'})

def reset_password(request):
    uidb64 = request.POST.get('uidb64', '')
    token = request.POST.get('token', '') 
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user_model = get_user_model()
        user = user_model.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    password = request.POST.get('password1', '')
    password2 = request.POST.get('password2', '')
    if password != password2:
        return JsonResponse({'status': 'error', 'message': 'Passwords do not match'}, status=400)
    prtg = PasswordResetTokenGenerator()
    if prtg.check_token(user, token):
        user.set_password(password)
        user.save()
        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid Form'}, status=400)

def request_activation_link(request):
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
            html_message = loader.render_to_string('emails/account_activation_email.html', email_context)
            text_message = loader.render_to_string('emails/account_activation_email.txt', email_context)
            send_mail(
                subject=email_subject,
                message=text_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                html_message=html_message,
                recipient_list=[user.email],
                fail_silently=False,
            )
            return JsonResponse({'status': 'success'})
        except Exception:
            return JsonResponse({'status': 'error', 'message': 'Could not resend activation link'}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid Form'}, status=400)

def activate(request):
    uidb64 = request.POST.get('uidb64', '')
    token = request.POST.get('token', '') 
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
        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Could not activate user account'}, status=400)


# static - not an endpoint
def send_new_token(request):
    device = EmailDevice.objects.get(user=request.user)
    current_site = get_current_site(request)
    # if current token is expired, generate a new one
    now = timezone.now()
    if now > device.valid_until:
        device.generate_token(valid_secs=settings.OTP_EMAIL_TOKEN_VALIDITY)
    email_subject = 'Carbure - Code de Sécurité'
    dt = device.valid_until.astimezone(pytz.timezone('Europe/Paris'))
    expiry = "%s %s" % (dt.strftime('%H:%M'), dt.tzname())
    email_context = {
        'user': request.user,
        'domain': current_site.domain,
        'token': device.token,
        'token_expiry': expiry,
    }
    html_message = loader.render_to_string('emails/otp_token_email.html', email_context)
    text_message = loader.render_to_string('emails/otp_token_email.txt', email_context)
    send_mail(
        subject=email_subject,
        message=text_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        html_message=html_message,
        recipient_list=[request.user.email],
        fail_silently=False,
    )

from django.contrib import admin
from django.contrib.auth import get_user_model, login, logout
from django.forms import CharField, Form, ValidationError
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.generic import TemplateView
from django_otp import login as otp_login
from django_otp.plugins.otp_email.models import EmailDevice


class OTPVerificationForm(Form):
    otp_token = CharField(
        max_length=6,
        required=True,
        widget=admin.widgets.AdminTextInputWidget(),
        label=_("Code de vérification"),
        help_text=_("Entrez le code à 6 chiffres reçu par email"),
    )

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.user_cache = None
        self.otp_device = None

    def clean(self):
        cleaned_data = super().clean()
        otp_token = cleaned_data.get("otp_token")

        if not otp_token:
            return cleaned_data

        user_id = self.request.session.get("otp_user_id")
        if not user_id:
            raise ValidationError(_("Session expirée. Veuillez recommencer la connexion."))

        try:
            User = get_user_model()
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise ValidationError(_("Utilisateur non trouvé."))

        device = EmailDevice.objects.filter(user=user, name="email").first()

        if not device:
            raise ValidationError(_("Code de vérification invalide ou expiré."))

        is_allowed, reason = device.verify_is_allowed()
        if not is_allowed:
            locked_until_utc = reason.get("locked_until")
            locked_until_local = timezone.localtime(locked_until_utc)
            formatted_time = locked_until_local.strftime("%H:%M:%S")
            failure_count = reason.get("failure_count", 0)

            raise ValidationError(
                _("Trop de tentatives incorrectes (%d échecs). Prochaine tentative possible à partir de %s.")
                % (failure_count, formatted_time)
            )

        now = timezone.now()
        if now > device.valid_until:
            raise ValidationError(_("Le code de sécurité a expiré. Veuillez demander un nouveau code."))

        if not device.verify_token(otp_token):
            raise ValidationError(_("Le code de sécurité est incorrect."))

        # Store user and device for login
        self.user_cache = user
        self.otp_device = device
        return cleaned_data


class OTPVerificationView(TemplateView):
    template_name = "admin/otp_verify.html"
    form_class = OTPVerificationForm

    @method_decorator(never_cache)
    @method_decorator(csrf_protect)
    def dispatch(self, request, *args, **kwargs):
        if not request.session.get("otp_user_id"):
            return redirect("admin:login")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = self.form_class(request)
        return self.render_to_response({"form": form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request, data=request.POST)
        if form.is_valid():
            user = form.user_cache
            login(request, user)
            otp_login(request, form.otp_device)

            if "otp_user_id" in request.session:
                del request.session["otp_user_id"]

            next_url = request.session.get("otp_next_url", reverse("admin:index"))
            if "otp_next_url" in request.session:
                del request.session["otp_next_url"]
            return HttpResponseRedirect(next_url)

        return self.render_to_response({"form": form})


def admin_otp_logout(request):
    logout(request)
    return redirect("admin:login")

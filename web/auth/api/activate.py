from django.contrib.auth import get_user_model, login
from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode

from auth.tokens import account_activation_token
from core.carburetypes import CarbureError
from core.common import ErrorResponse, SuccessResponse


def activate(request):
    uidb64 = request.POST.get("uidb64", "")
    token = request.POST.get("token", "")
    invite = request.POST.get("invite", 0)
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user_model = get_user_model()
        user = user_model.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)

        data = {}

        if invite:
            # Generate token to let new user change his password
            prtg = PasswordResetTokenGenerator()
            passtoken = prtg.make_token(user)
            data = {"token": passtoken}

        return SuccessResponse(data=data)
    else:
        # return JsonResponse({'status': 'error', 'message': 'Could not activate user account'}, status=400)
        return ErrorResponse(400, CarbureError.ACTIVATION_COULD_NOT_ACTIVATE_USER)

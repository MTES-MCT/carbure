from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode

from core.carburetypes import CarbureError
from core.common import ErrorResponse, SuccessResponse


def reset_password(request):
    uidb64 = request.POST.get("uidb64", "")
    token = request.POST.get("token", "")
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user_model = get_user_model()
        user = user_model.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    password = request.POST.get("password1", "")
    password2 = request.POST.get("password2", "")
    if password != password2:
        # return JsonResponse({'status': 'error', 'message': 'Passwords do not match'}, status=400)
        return ErrorResponse(400, CarbureError.PASSWORD_RESET_MISMATCH)
    prtg = PasswordResetTokenGenerator()
    if prtg.check_token(user, token):
        user.set_password(password)
        user.save()
        # return JsonResponse({'status': 'success'})
        return SuccessResponse()
    else:
        # return JsonResponse({'status': 'error', 'message': 'Invalid Form'}, status=400)
        return ErrorResponse(400, CarbureError.PASSWORD_RESET_INVALID_FORM)

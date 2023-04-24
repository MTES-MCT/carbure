from core.carburetypes import CarbureError
from core.common import ErrorResponse, SuccessResponse
from django.contrib.auth import authenticate
from django.contrib.auth import login


def user_login(request):
    username = request.POST.get("username", "")
    password = request.POST.get("password", "")
    user = authenticate(username=username, password=password)
    login(request, user)
    try:
        if user.is_authenticated:
            request.session.set_expiry(3 * 30 * 24 * 60 * 60)  # 3 months
            # return JsonResponse({'status': 'success', 'message': 'User logged in'})
            return SuccessResponse()
        else:
            # return JsonResponse({'status': 'error', 'message': 'Invalid credentials'}, status=400)
            return ErrorResponse(400, CarbureError.INVALID_LOGIN_CREDENTIALS)
    except:
        # return JsonResponse({'status': 'error', 'message': 'Account not activated'}, status=400)
        return ErrorResponse(400, CarbureError.ACCOUNT_NOT_ACTIVATED)

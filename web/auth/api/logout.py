from django.contrib.auth import logout

from core.common import SuccessResponse


def user_logout(request):
    logout(request)
    # return JsonResponse({'status': 'success'})
    return SuccessResponse()

from core.common import SuccessResponse
from django.contrib.auth import logout


def user_logout(request):
    logout(request)
    # return JsonResponse({'status': 'success'})
    return SuccessResponse()

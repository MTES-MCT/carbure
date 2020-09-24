from django.http import JsonResponse


def get_users(request):
    return JsonResponse({"status": "error", "message": "Not implemented"}, status=400)


def get_entities():
    return JsonResponse({"status": "error", "message": "Not implemented"}, status=400)


def get_rights():
    return JsonResponse({"status": "error", "message": "Not implemented"}, status=400)

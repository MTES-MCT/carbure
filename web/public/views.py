from django.shortcuts import redirect

def redirect_app(request, path):
    return redirect("/" + path, permanent=True)

from django.shortcuts import redirect


# redirect calls starting with /app to / and keep all query params
def redirect_app(request, path):
    url = "/" + path
    params = request.META["QUERY_STRING"]
    if params:
        url += "?" + params
    return redirect(url, permanent=True)

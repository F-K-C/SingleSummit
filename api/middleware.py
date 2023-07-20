class CommonMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if hasattr(request, "user") and not  request.user.is_anonymous:
            bearer = request.META.get("HTTP_AUTHORIZATION", "")
            if bearer.startswith("Bearer") and bearer.split("Bearer")[1] != " ":
                request.user.fcm = request.META.get("HTTP_FCM_TOKEN", "")
                request.user.save()
        response = self.get_response(request)
        return response

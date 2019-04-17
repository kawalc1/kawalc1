from django.http import HttpResponse

from kawalc1 import settings


class AuthenticationMiddleware(object):

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        auth = request.META.get('HTTP_AUTHORIZATION')
        return self.get_response(request) if (settings.SECRET == auth or not settings.AUTHENTICATION_ENABLED) else HttpResponse('Unauthorized', status=401)


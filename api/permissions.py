from django.contrib.auth import authenticate
from oauth2_provider.models import AccessToken
from rest_framework import permissions
from rest_framework.exceptions import NotAuthenticated
from rest_framework.response import Response
from rest_framework.views import exception_handler

from api.users.models import AccessLevel


class BaseAuthPermission(permissions.BasePermission):

    def verify_header(self, request):
        if request.META.get("HTTP_AUTHORIZATION", "").startswith("Bearer"):
            if not hasattr(request, "user") or request.user.is_anonymous:
                user = authenticate(request=request)
                if user:
                    request.user = request._cached_user = user
                    # request.data['created_by'] = request.user.id
                    return True
        return False

    def verify_cookie(self, request):
        try:
            access_token = request.COOKIES.get('u-at', None)
            if access_token:
                request.user = AccessToken.objects.get(token=access_token).user
                request.user.access_token = access_token
                # request.data['created_by'] = request.user.id
                return True
            else:
                return False
        except AccessToken.DoesNotExist:
            return False


class IsAuthenticated(BaseAuthPermission):

    def has_permission(self, request, view):
        # allow all POST requests

        if request.META.get("HTTP_AUTHORIZATION", "").startswith("Bearer"):
            if not hasattr(request, "user") or request.user.is_anonymous:
                user = authenticate(request=request)
                if user:
                    request.user = request._cached_user = user
                    return True
                return False
        else:
            try:
                access_token = request.COOKIES.get('u-at', None)
                if access_token:
                    request.user = AccessToken.objects.get(token=access_token).user
                    request.user.access_token = access_token
                    # request.data['created_by'] = request.user.id
                    return True
                else:
                    return False
            except AccessToken.DoesNotExist:
                return False


class IsClientAuthenticated(BaseAuthPermission):

    def has_permission(self, request, view):
        # allow all POST requests

        if request.META.get("HTTP_AUTHORIZATION", "").startswith("Bearer"):
            if not hasattr(request, "user") or request.user.is_anonymous:
                user = authenticate(request=request)
                if user.role.code == AccessLevel.CLIENT_CODE:
                    request.user = request._cached_user = user
                    return True
                return False
        else:
            try:
                access_token = request.COOKIES.get('u-at', None)
                if access_token:
                    request.user = AccessToken.objects.get(token=access_token).user
                    request.user.access_token = access_token
                    # request.data['created_by'] = request.user.id
                    return True
                else:
                    return False
            except AccessToken.DoesNotExist:
                return False


class IsGETorClientAuthenticated(BaseAuthPermission):

    def has_permission(self, request, view):
        # allow all POST requests
        if request.method == "GET":
            return True
        if request.META.get("HTTP_AUTHORIZATION", "").startswith("Bearer"):
            if not hasattr(request, "user") or request.user.is_anonymous:
                user = authenticate(request=request)
                if user.role.code == AccessLevel.CLIENT_CODE:
                    request.user = request._cached_user = user
                    return True
                return False
        else:
            try:
                access_token = request.COOKIES.get('u-at', None)
                if access_token:
                    request.user = AccessToken.objects.get(token=access_token).user
                    request.user.access_token = access_token
                    # request.data['created_by'] = request.user.id
                    return True
                else:
                    return False
            except AccessToken.DoesNotExist:
                return False


def custom_exception_handler(exc, context):
    if isinstance(exc, NotAuthenticated):
        return Response({"description": "Authentication credentials were not provided."},
                        status=401)

    # else
    # default case
    return exception_handler(exc, context)

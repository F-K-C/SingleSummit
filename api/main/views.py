import json
import secrets
from datetime import timezone, timedelta, datetime

import requests
from django.conf import settings
from django.contrib.sessions.backends.db import SessionStore
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

from oauth2_provider.models import get_access_token_model, get_application_model
from django.contrib.auth import login as login_auth, authenticate

from api.users.serializers import UserSerializer

AccessToken = get_access_token_model()
Application = get_application_model()

# Create your views here.
from oauthlib.oauth2.rfc6749.tokens import random_token_generator

from api.users.models import User, Role, AccessLevel


def authorize_google(request):
    """
    :param request:
    :return:
    """
    # Redirect users to Google sign-in page for authorization
    # Contains Permissions for email, profile, openid and google photos
    authorization_url = f"https://accounts.google.com/o/oauth2/v2/auth?response_type=code&client_id={settings.GOOGLE_CLIENT_ID}&redirect_uri={settings.REDIRECT_URL}&scope=openid email profile"
    return redirect(authorization_url)


def google_auth_callback(request):
    """
    :param request:
    :return:
    """
    # Handle the callback URL after user authorization
    code = request.GET.get('code')
    if code:
        # Exchange authorization code for an access token
        token_endpoint = 'https://accounts.google.com/o/oauth2/token'
        token_params = {
            'code': code,
            'client_id': settings.GOOGLE_CLIENT_ID,
            'client_secret': settings.GOOGLE_CLIENT_SECRET,
            'redirect_uri': settings.REDIRECT_URL,
            'grant_type': 'authorization_code'
        }
        response = requests.post(token_endpoint, data=token_params)
        if response.status_code == 200:
            token_data = response.json()
            access_token, token_id = token_data['access_token'], token_data['id_token']

            # Verify the access token
            try:
                id_info = id_token.verify_oauth2_token(
                    token_id, google_requests.Request(), settings.GOOGLE_CLIENT_ID, clock_skew_in_seconds=10
                )
                if id_info['iss'] == 'accounts.google.com' and id_info['aud'] == settings.GOOGLE_CLIENT_ID:
                    # Access token is valid, make API requests
                    # Process to Fetch and Save User Data
                    user = fetch_client_email(access_token, token_id, request)
                    # Set the Token Id in client browser as a cookie
                    token = generate_access_token_password_grant(user)
                    serialized = UserSerializer(user)
                    user_data = serialized.data
                    user_data['access_token'] = token.token
                    user_data['refresh_token'] = token.token
                    user.backend = 'django.contrib.auth.backends.AllowAllUsersModelBackend'
                    login_auth(request, user)
                    # Return the session ID or any other relevant data
                    # return HttpResponseRedirect(reverse('social_login'))
                    response = redirect("/")
                    response.set_cookie('u-at', token.token)
                    return response
                else:
                    return HttpResponseBadRequest("Invalid access token.")
            except ValueError as e:
                return HttpResponseBadRequest("Failed to verify access token.")
        else:
            return HttpResponseBadRequest("Failed to exchange authorization code for access token.")
    else:
        return HttpResponseBadRequest("Authorization code not provided.")


def fetch_client_email(access_token, token_id, request):
    """
    :param access_token:
    :param token_id:
    :return:
    """
    # Fetch User Detail after authorization and update token
    endpoint = 'https://openidconnect.googleapis.com/v1/userinfo'
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(endpoint, headers=headers)
    if response.status_code == 200:
        user_scope = response.json()
        user_instance = User.objects.get_or_create(
            email=user_scope['email'],
        )
        if user_instance[1]:
            user_instance[0].first_name = user_scope['given_name']
            user_instance[0].last_name = user_scope['family_name']
            user_instance[0].is_email_verified = True
            user_instance[0].role = Role.objects.get(code__exact=AccessLevel.CLIENT_CODE)
            user_instance[0].save()
        return user_instance[0]
    else:
        return None


def generate_access_token_password_grant(instance):
    # Replace 'your_client_id' and 'your_client_secret' with your actual client credentials
    application = Application.objects.filter().first()

    token = AccessToken.objects.create(
        user=instance,  # For password grant, user is None
        application=application,
        expires=datetime.now() + timedelta(days=365),
        token=secrets.token_hex(32),
        scope="read write"
    )
    return token
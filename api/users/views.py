from datetime import datetime

import requests
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth import logout
from django.core.exceptions import FieldError
from django.db import transaction
from django.db.models import Prefetch, Q
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect
from django.utils.translation import gettext as _
from model_utils import Choices
from rest_framework import status
from rest_framework.authentication import TokenAuthentication

from api.main.views import generate_access_token_password_grant
from api.permissions import IsAuthenticated
from api.users.models import User, EmailVerificationLink, Role, AccessLevel
from api.users.serializers import AuthenticateSerializer, UserSerializer
from api.views import BaseAPIView
from single_summit_app.utils import parse_email, query_datatable_by_args_transaction
from django.contrib.auth import login as login_auth
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token


class UserProfilePasswordView(BaseAPIView):
    """
    API View for Login Super Admin and Admin
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk=None):
        """
        In this api, only **Super Admin** and **Local Admin** can login. Other users won't be able to login through this API.
        **Mandatory Fields**
        * email
        * password
        """
        try:
            user_data = User.objects.get(id=request.user.id)
            if not request.data['new_password']:
                return self.send_response(
                    success=True,
                    code=f'422',
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    description=_("Password Required")
                )
            else:
                if user_data.check_password(request.data['old_password']):
                    user_data.set_password(request.data['new_password'])
                    user_data.save()
                    # user = User
                    return self.send_response(
                        success=True,
                        code=f'200',
                        status_code=status.HTTP_200_OK,
                        description=_("Password Updated Successfully")
                    )
                else:
                    return self.send_response(
                        success=True,
                        code=f'422',
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        description=_("Invalid Password")
                    )
        except User.DoesNotExist:
            return self.send_response(
                code=f'422',
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description=_("User doesn't exist")
            )
        except FieldError:
            return self.send_response(
                code=f'500',
                description=_("Cannot resolve keyword given in 'order_by' into field")
            )
        except Exception as e:
            if hasattr(e.__cause__, 'pgcode') and e.__cause__.pgcode == '23505':
                return self.send_response(
                    code=f'422',
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    description=_("Um usuário com esse email já existe no sistema.")
                )
            else:
                return self.send_response(
                    code=f'500',
                    description=e
                )


class LoginSuperAdminView(BaseAPIView):
    """
    API View for Login Super Admin and Admin
    """
    authentication_classes = ()
    permission_classes = ()

    def post(self, request, pk=None):
        try:
            serializer = AuthenticateSerializer(data=request.data)
            if serializer.is_valid():
                email = parse_email(serializer.data.get('email'))
                password = serializer.data.get('password')
                user = authenticate(request, email=email, password=password)
                if user:
                    if user.is_active:
                        oauth_token = self.get_oauth_token(email, password)
                        if 'access_token' in oauth_token:
                            serialized = UserSerializer(User.objects.get(id=user.id))
                            user_data = serialized.data
                            user_data['access_token'] = oauth_token.get('access_token')
                            user_data['refresh_token'] = oauth_token.get('refresh_token')
                            login_auth(request, user)
                            return self.send_response(success=True,
                                                      code=f'200',
                                                      status_code=status.HTTP_200_OK,
                                                      payload=user_data,
                                                      description=_('You are logged in!'),
                                                      log_description=_(
                                                          f'User {user_data["email"]}. with id .{user_data["id"]}. has just logged in.')
                                                      )
                        else:
                            return self.send_response(
                                description=_('Something went wrong with Oauth token generation.'),
                                code=f'500')
                    else:
                        description = _('Your account is blocked or deleted.')
                        return self.send_response(success=False,
                                                  code=f'422',
                                                  status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                                  payload={},
                                                  description=description)
                else:
                    return self.send_response(
                        success=False,
                        code=f'422',
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        payload={}, description=_('Email or password is incorrect.')
                    )
            else:
                return self.send_response(
                    success=False,
                    code='422',
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    description=serializer.errors
                )


        except Exception as e:
            return self.send_response(code=f'500',
                                      description=e)


class RegisterView(BaseAPIView):
    """
    API View for Login Super Admin and Admin
    """
    authentication_classes = ()
    permission_classes = ()

    def post(self, request, pk=None):
        try:
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                validated_data = serializer.validated_data
                validated_data['role'] = Role.objects.get(code=AccessLevel.CLIENT_CODE)
                serializer.save(**validated_data)
                password = request.data.get('password')
                email = parse_email(request.data.get('email'))
                serializer.instance.set_password(password)
                serializer.instance.save()
                user = authenticate(request, email=email, password=password)
                if serializer.instance:
                    if serializer.instance.is_active:
                        oauth_token = self.get_oauth_token(email, password)
                        if 'access_token' in oauth_token:
                            user_data = UserSerializer(serializer.instance).data
                            user_data['access_token'] = oauth_token.get('access_token')
                            user_data['refresh_token'] = oauth_token.get('refresh_token')
                            login_auth(request, user)
                            return self.send_response(success=True,
                                                      code=f'200',
                                                      status_code=status.HTTP_200_OK,
                                                      payload=user_data,
                                                      description='You are logged in!',
                                                      )
                        else:
                            return self.send_response(description='Something went wrong with Oauth token generation.',
                                                      code=f'500')
                    else:
                        description = 'Your account is blocked or deleted.'
                        return self.send_response(success=False,
                                                  code=f'422',
                                                  status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                                  payload={},
                                                  description=description)
                else:
                    return self.send_response(
                        success=False,
                        code=f'422',
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        payload={}, description='Email or password is incorrect.'
                    )
            else:
                return self.send_response(
                    success=False,
                    code='422',
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    description=serializer.errors
                )
        except Exception as e:
            if hasattr(e.__cause__, 'pgcode') and e.__cause__.pgcode == '23505':
                return self.send_response(
                    code=f'422',
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    description="Um usuário com esse email já existe no sistema."
                )
            return self.send_response(
                code=f'500',
                description=e
            )


class UserView(BaseAPIView):
    """
    API View for Login Super Admin and Admin
    """
    authentication_classes = ()
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk=None):
        try:
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                validated_data = serializer.validated_data
                validated_data['role'] = Role.objects.get(code=AccessLevel.CLIENT_CODE)
                serializer.save(**validated_data)
                password = request.data.get('password')
                email = parse_email(request.data.get('email'))
                serializer.instance.set_password(password)
                serializer.instance.save()
                return self.send_response(
                    success=True,
                    code=f'200',
                    status_code=status.HTTP_200_OK,
                    description='User Created Successfully',
                )
            else:
                return self.send_response(
                    success=False,
                    code='422',
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    description=serializer.errors
                )
        except Exception as e:
            if hasattr(e.__cause__, 'pgcode') and e.__cause__.pgcode == '23505':
                return self.send_response(
                    code=f'422',
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    description="Um usuário com esse email já existe no sistema."
                )
            return self.send_response(
                code=f'500',
                description=e
            )

    def put(self, request, pk=None):
        try:
            instance = User.objects.get(id=pk)
            serializer = UserSerializer(data=request.data, instance=instance)
            if serializer.is_valid():
                serializer.save()
                return self.send_response(
                    success=True,
                    code=f'200',
                    status_code=status.HTTP_200_OK,
                    description='User Updated Successfully',
                )
            else:
                return self.send_response(
                    success=False,
                    code='422',
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    description=serializer.errors
                )
        except Exception as e:
            if hasattr(e.__cause__, 'pgcode') and e.__cause__.pgcode == '23505':
                return self.send_response(
                    code=f'422',
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    description="Um usuário com esse email já existe no sistema."
                )
            return self.send_response(
                code=f'500',
                description=e
            )


class UserDataTableAPIView(BaseAPIView):
    """
    API View for Login Super Admin and Admin
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk=None):
        """
        :param request:
        :param pk: to get singal instance of property
        :return: response of required properties listings
        """
        try:
            query_object = Q(role__code=AccessLevel.CLIENT_CODE)
            ORDER_COLUMN_CHOICES = Choices(
                ('0', 'id'),
                ('1', 'type'),
                ('4', 'id'),
                ('6', 'description'),
                ('7', 'price')
            )
            property_ = query_datatable_by_args_transaction(
                kwargs=request.query_params,
                model=User,
                query_object=query_object,
                ORDER_COLUMN_CHOICES=ORDER_COLUMN_CHOICES,
                search_function=self.search_user
            )

            serializer = UserSerializer(property_.get('items', []), many=True)

            property_data = {
                'draw': property_.get('draw', 0),
                'recordsTotal': property_.get('total', 0),
                'recordsFiltered': property_.get('count', 0),
                'data': serializer.data,
            }
            description = 'List of jobs'

            return self.send_response(
                success=True,
                status_code=status.HTTP_200_OK,
                payload=property_data,
                description=description
            )

        except User.DoesNotExist as e:
            return self.send_response(
                code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description=str(e)
            )
        except Exception as e:
            return self.send_response(
                code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                description=str(e)
            )

    @staticmethod
    def search_user(queryset, search_value, kwargs):
        """
        search given queryset with given search_value
        :param list queryset: all records of a model
        :param str search_value: value user enter in datatable search
        :param dict kwargs: request param from datatable
        :rtype:list
        """
        try:
            query_object = Q(first_name__icontains=search_value) | Q(last_name__icontains=search_value)
            query_object |= Q(email__icontains=search_value)
            return queryset.filter(query_object)
        except:
            return []


class UserStatusAPIView(BaseAPIView):
    """
    API View for Login Super Admin and Admin
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk=None):
        """
        :param request:
        :param pk: to get singal instance of property
        :return: response of required properties listings
        """
        try:
            instance = User.objects.get(id=pk)
            instance.is_active = not instance.is_active
            instance.save()
            if instance.is_active:
                message = "User Activated Successfully"
            else:
                message = "User Disabled Successfully"
            return self.send_response(
                success=True,
                status_code=status.HTTP_200_OK,
                description=message
            )
        except User.DoesNotExist as e:
            return self.send_response(
                code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="User does not exist in our system."
            )
        except Exception as e:
            return self.send_response(
                code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                description=str(e)
            )

    @staticmethod
    def search_transaction(queryset, search_value, kwargs):
        """
        search given queryset with given search_value
        :param list queryset: all records of a model
        :param str search_value: value user enter in datatable search
        :param dict kwargs: request param from datatable
        :rtype:list
        """
        try:
            query_object = Q(first_name__icontains=search_value) | Q(last_name__icontains=search_value)
            query_object |= Q(email__icontains=search_value)
            return queryset.filter(query_object)
        except:
            return []


class UserDeleteAPIView(BaseAPIView):
    """
    API View for Login Super Admin and Admin
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk=None):
        """
        :param request:
        :param pk: to get singal instance of property
        :return: response of required properties listings
        """
        try:
            User.objects.get(id=pk).delete()
            return self.send_response(
                success=True,
                status_code=status.HTTP_200_OK,
                description="User Deleted Successfully"
            )
        except User.DoesNotExist as e:
            return self.send_response(
                code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="User does not exist in our system."
            )
        except Exception as e:
            return self.send_response(
                code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                description=str(e)
            )

    @staticmethod
    def search_transaction(queryset, search_value, kwargs):
        """
        search given queryset with given search_value
        :param list queryset: all records of a model
        :param str search_value: value user enter in datatable search
        :param dict kwargs: request param from datatable
        :rtype:list
        """
        try:
            query_object = Q(first_name__icontains=search_value) | Q(last_name__icontains=search_value)
            query_object |= Q(email__icontains=search_value)
            return queryset.filter(query_object)
        except:
            return []


class LogoutView(BaseAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()

    def get(self, request):
        try:
            token = request.META.get("HTTP_AUTHORIZATION", "").replace("Bearer ", "")
            if not self.revoke_oauth_token(token):
                return self.send_response(code=f'422',
                                          status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                          description=_("User doesn't logout")
                                          )
            logout(request)
            return self.send_response(success=True,
                                      code=f'201', status_code=status.HTTP_201_CREATED,
                                      payload={},
                                      description=_('User logout successfully')
                                      )
        except User.DoesNotExist:
            return self.send_response(code=f'422',
                                      status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      description=_("User doesn't exists")
                                      )
        except FieldError:
            return self.send_response(code=f'500',
                                      description=_("Cannot resolve keyword given in 'order_by' into field")
                                      )
        except Exception as e:
            return self.send_response(code=f'500',
                                      description=e)


class VerifyInvitationLink(BaseAPIView):
    """
    Verify the Link of the Local Admin
    """
    authentication_classes = ()
    permission_classes = ()

    def post(self, request, pk=None):
        """
        In this API, we will validate the **Local Admin** token. Whether it is a valid token, or unexpired.
        If it is, it will return the user_id using which **Local Admin** will update his/her password
        """
        try:
            verify = EmailVerificationLink.objects.get(token=request.data['token'], code=request.data['code'])
            if datetime.date(verify.expiry_at) <= datetime.date(datetime.now()):
                EmailVerificationLink.add_email_token_link(verify.user)
                verify.delete()
                return self.send_response(
                    code=f'422',
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    description=_("The link is expired. New link has been sent to your email")
                )
            else:
                return self.send_response(
                    success=True,
                    code=f'201',
                    status_code=status.HTTP_201_CREATED,
                    payload={"user_id": verify.user_id},
                    description=_("Token Verified Successfully")
                )
        except EmailVerificationLink.DoesNotExist:
            return self.send_response(
                code=f'422',
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description=_("Verification token doesn't exists")
            )
        except Exception as e:
            return self.send_response(
                code=f'500',
                description=e
            )


class UpdatePassword(BaseAPIView):
    authentication_classes = ()
    permission_classes = ()

    def post(self, request, pk=None):
        """
        In this API, we will validate the **Local Admin** token. Whether it is a valid token, or unexpired.
        If it is, it will return the user_id using which **Local Admin** will update his/her password
        """
        try:
            verify = EmailVerificationLink.objects.get(token=request.data['token'], code=request.data['code'])
            if datetime.date(verify.expiry_at) <= datetime.date(datetime.now()):
                EmailVerificationLink.add_email_token_link(verify.user)
                verify.delete()
                return self.send_response(
                    code=f'422',
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    description=_("The link is expired. New link has been sent to your email")
                )
            else:
                verify.user.set_password(request.data["password"])
                verify.user.save(update_fields=["password"])
                verify.delete()
            return self.send_response(
                success=True,
                code=f'201',
                status_code=status.HTTP_201_CREATED,
                description=_("Password Updated")
            )
        except EmailVerificationLink.DoesNotExist:
            return self.send_response(
                code=f'422',
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description=_("Verification token doesn't exists")
            )
        except Exception as e:
            return self.send_response(
                code=f'500',
                description=e
            )


class ForgotPasswordView(BaseAPIView):
    parser_class = ()
    authentication_classes = ()
    permission_classes = ()

    def post(self, request, pk=None):
        try:
            if request.data['email'] == "" or None:
                return self.send_response(
                    code=f'422',
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    description=_("Email required")
                )
            else:
                user = User.objects.get(email__exact=parse_email(request.data['email']))
                obj = EmailVerificationLink.add_email_token_link(user)
                return self.send_response(
                    success=True,
                    code=f'201',
                    payload={"key": obj.token,
                             },
                    status_code=status.HTTP_201_CREATED,
                    description=_("Forgot Password mail sent successfully"),
                )
        except User.DoesNotExist:
            return self.send_response(
                code=f'422',
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description=_("User does not exists")
            )
        except Exception as e:
            return self.send_response(
                code=f'500',
                description=e
            )


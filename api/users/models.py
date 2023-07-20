import random
from datetime import datetime, timedelta
from uuid import uuid4

from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
# Create your models here.
from rest_framework.authtoken.models import Token
from slugify import slugify

from main.models import Log
from single_summit_app.utils import parse_email
from django.utils.translation import gettext_lazy as _


# Create your models here.

class AccessLevel:
    """
    Access levels for user roles.
    """
    CLIENT = 500
    SUPER_ADMIN = 900

    CLIENT_CODE = 'client'
    SUPER_ADMIN_CODE = 'super-admin'

    CHOICES = (
        (CLIENT, "Client"),
        (SUPER_ADMIN, 'Super Admin'),
    )

    CODES = (
        (CLIENT, "client"),
        (SUPER_ADMIN, 'super-admin')
    )
    DICT = dict(CHOICES)
    CODES_DICT = dict(CODES)


class Role(Log):
    """ Role model."""
    name = models.CharField(db_column='Name', max_length=255, unique=True)
    code = models.SlugField(db_column='Code', default='')
    description = models.TextField(db_column='Description', null=True, blank=True)
    access_level = models.IntegerField(db_column='AccessLevel', choices=AccessLevel.CHOICES,
                                       default=AccessLevel.CLIENT_CODE)

    class Meta:
        db_table = 'Roles'

    def __str__(self):
        return f'{self.name}'

    def save(self, *args, **kwargs):
        try:
            if not self.pk:
                self.code = slugify(self.name)
            super().save()
        except Exception:
            raise

    @staticmethod
    def get_role_by_code(code=None):
        try:
            return Role.objects.get(code__exact=code)
        except Exception as e:
            print(e)
            return e


class CustomAccountManager(BaseUserManager):

    def create_user(self, email, password):
        user = self.model(email=email, password=password)
        passw = password
        user.set_password(passw)
        user.is_superuser = False
        user.is_approved = False
        user.is_active = False
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(email=email, password=password)
        passw = password
        user.set_password(passw)
        user.is_superuser = True
        user.is_approved = True
        user.is_active = True
        user.role = Role.objects.get(code=AccessLevel.SUPER_ADMIN_CODE)
        # Group.objects.get_or_create(name='Super_Admin')
        # user.groups.add(Super_Admin)
        user.save()
        return user


class User(AbstractBaseUser, Log, PermissionsMixin):
    """ User model."""
    first_name = models.TextField(db_column='FirstName', default="")
    # middle_name = models.TextField(db_column='MiddleName', default="")
    last_name = models.TextField(db_column='LastName', default="")
    is_active = models.BooleanField(
        db_column='IsActive',
        default=False,
        help_text='Designates whether this user should be treated as active. '
                  'Unselect this instead of deleting accounts.',
    )
    is_approved = models.BooleanField(
        db_column='IsApproved',
        default=True,
        help_text='Designates whether this user is approved or not.',
    )
    email = models.EmailField(unique=True, db_column="Email", help_text="Email Field")
    username = models.CharField(default=None, db_column="Username", null=True, blank=True, max_length=255)
    is_email_verified = models.BooleanField(db_column='IsEmailVerified', default=False)
    role = models.ForeignKey(Role, db_column='RoleId', related_name='user_role', on_delete=models.CASCADE, default="",
                             null=True, blank=True)
    is_staff = models.BooleanField(
        default=True,
        help_text='Designates whether the user can log into this admin site.',
    )
    is_deleted = models.BooleanField(
        default=False,
        db_column='IsDeleted'
    )
    fcm = models.TextField(db_column="FCM", null=True, default=None)
    # search_vector = SearchVectorField(null=True)
    # image = models.ImageField(upload_to=image_directory_path, null=True)
    # bio = models.TextField(db_column='Bio', null=True)
    # no_visiting = models.IntegerField(default=0)
    objects = CustomAccountManager()
    # objects = UserSearchManager()
    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'

    class Meta:
        db_table = 'Users'

    # def __str__(self):
    #     return f'{self.first_name}'

    def save(self, *args, **kwargs):
        try:
            if not self.pk:
                self.email = parse_email(self.email)
            super().save()
        except Exception:
            raise


class EmailVerificationLink(Log):
    token = models.CharField(db_column='Token', primary_key=True, unique=True, max_length=255)
    code = models.IntegerField(db_column="Code", null=True, blank=True, default=None)
    user = models.ForeignKey(User, db_column='UserId', related_name='user_id', on_delete=models.CASCADE)
    expiry_at = models.DateTimeField(db_column='ExpireAt')

    class Meta:
        db_table = "Email_Verification"

    def save(self, *args, **kwargs):
        try:
            if not self.pk:
                self.token = uuid4()
                self.code = random.randint(1000, 9999)
            super().save()
        except Exception:
            raise

    @staticmethod
    def add_email_token_link(user):
        try:
            object = {"user": user, "expiry_at": datetime.now() + timedelta(+5)}
            email_link = EmailVerificationLink.objects.create(**object)
            print(email_link)

            # send_email_sendgrid_template(
            #     from_email=settings.CONTACT_US_EMAIL,
            #     to_email=user.email,
            #     subject="Forgot Password",
            #     data=data,
            #     template=settings.FORGOT_PASSWORD_TEMPLATE_ID
            # )
            return email_link
        except Exception as e:
            return e

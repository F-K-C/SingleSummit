# Create your views here.
from django.urls import path

# app_name will help us do a reverse look-up latter.
from api.users.views import LoginSuperAdminView, RegisterView, UserDataTableAPIView, UserStatusAPIView, \
    UserDeleteAPIView, UserView, LogoutView

urlpatterns = [

    path("", UserView.as_view(), name="users"),
    path("<int:pk>", UserView.as_view(), name="users"),

    path("login", LoginSuperAdminView.as_view(), name="users_admin_login"),
    path("register", RegisterView.as_view(), name="users_admin_register"),

    path("datatable", UserDataTableAPIView.as_view(), name="users_datatable"),

    path("status", UserStatusAPIView.as_view(), name="users_status"),
    path("status/<int:pk>", UserStatusAPIView.as_view(), name="users_status"),

    path("delete", UserDeleteAPIView.as_view(), name="users_delete"),
    path("delete/<int:pk>", UserDeleteAPIView.as_view(), name="users_delete"),

    path("logout", LogoutView.as_view(), name='logout'),

]

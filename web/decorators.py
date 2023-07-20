from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth import logout


def logout_required(function=None, logout_url=""):
    actual_decorator = user_passes_test(
        lambda u: not u.is_authenticated,
        login_url=logout_url
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def superuser_required(function=None, redirect_url=""):
    actual_decorator = user_passes_test(
        lambda u: u.is_superuser,
        login_url=redirect_url
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def staff_required(function=None, redirect_url=""):
    actual_decorator = user_passes_test(
        lambda u: u.is_staff,
        login_url=redirect_url
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

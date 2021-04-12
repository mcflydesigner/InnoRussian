from functools import wraps
from django.shortcuts import redirect
from django.http import HttpRequest

def not_authorized_user(redirectTo='core:main'):
    """
        A function that returns decorator which checks that user is not authorized.
        Otherwise, it redirects user to the value of `redirectTo` variable.
    """
    def decorator(function):
        @wraps(function)
        def wrapped(*args, **kwargs):
            for arg in args:
                if isinstance(arg, HttpRequest):
                    request = arg
                    break
            else:
                raise ValueError('Argument request(instance of HttpRequest) must be provided')

            if not request.user.is_anonymous:
                return redirect(redirectTo)
            else:
                return function(*args, **kwargs)

        return wrapped

    return decorator

default_not_authorized = not_authorized_user()

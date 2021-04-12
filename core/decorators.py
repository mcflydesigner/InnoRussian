from functools import wraps
from django.http import (HttpRequest,
                         HttpResponse)

def login_require_or_401(function):
    """
        Decorator which check that the user is authorized.
        Otherwise, return status code 401.
    """
    @wraps(function)
    def wrapped(*args, **kwargs):
        for arg in args:
            if isinstance(arg, HttpRequest):
                request = arg
                break
        else:
            raise ValueError('Argument request(instance of HttpRequest) must be provided')

        if request.user.is_authenticated:
            return function(*args, **kwargs)
        else:
            return HttpResponse(status=401)

    return wrapped


def for_all_methods(decorator, exclude=None):
    """
        Decorator which wraps all methods of the object.
        However, it is possible not to wrap exactly all
        methods using `exclude` argument.
    """
    if not exclude:
        # By default is empty list, so, decorate all methods
        exclude = list()

    def decorate(cls):
        for attr in cls.__dict__:
            if callable(getattr(cls, attr)) and attr not in exclude:
                setattr(cls, attr, decorator(getattr(cls, attr)))
        return cls
    return decorate

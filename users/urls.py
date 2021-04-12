from django.urls import path

from .views import (SignInView,
                    SignUpView,
                    LogoutView,
                    PasswordResetView,
                    PasswordResetConfirmView)

app_name = 'users'

urlpatterns = [
    path('sign_in/', SignInView.as_view(), name='sign-in'),
    path('sign_up/', SignUpView.as_view(), name='sign-up'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('password-reset/', PasswordResetView.as_view(), name='password-reset'),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
]
from django.shortcuts import render
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.utils.http import (urlsafe_base64_encode,
                               urlsafe_base64_decode)
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes, force_text
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse


from .decorators import default_not_authorized
from .forms import (UserSignInForm,
                    UserSignUpForm,
                    PasswordResetForm,
                    PasswordResentConfirmForm)



class SignInView(View):
    """ View to login. """

    def get(self, request):
        form = UserSignInForm()

        return render(request, 'users/sign_in.html', context={'form': form})

    def post(self, request):
        form = UserSignInForm(request.POST)

        if form.is_valid():
            user = authenticate(request, username=form.cleaned_data['email'],
                                password=form.cleaned_data['password'])

            if user:
                login(request, user)
                return redirect('core:category-list')
            else:
                messages.error(request, 'Incorrect email or password :(')

        return render(request, 'users/sign_in.html', context={'form': form})

    # The user must be not authorized to access this view
    @method_decorator(default_not_authorized)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)





class SignUpView(View):
    """ View to create an account. """

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('core:main')

        form = UserSignUpForm()

        return render(request, 'users/sign_up.html', context={'form': form})

    def post(self, request):
        form = UserSignUpForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)

            try:
                validate_password(form.cleaned_data['password'], user)
            except (ValidationError, ValueError) as e:
                form.add_error('password', e)
            else:
                form.save()

                user = authenticate(request, username=form.cleaned_data['email'],
                                    password=form.cleaned_data['password'])
                if user:
                    login(request, user)

                return redirect('core:category-list')

        return render(request, 'users/sign_up.html', context={'form': form})

    # The user must be not authorized to access this view
    @method_decorator(default_not_authorized)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)




class LogoutView(View):
    """ View to logout. """

    def get(self, request):
        logout(request)
        messages.success(request, 'You successfully logout!')
        return redirect('/')




class PasswordResetView(View):
    """ View to reset the password of an account. """

    def get(self, request):
        form = PasswordResetForm()

        return render(request, 'users/reset_password.html', context={'form': form})

    def post(self, request):
        form = PasswordResetForm(request.POST)

        if form.is_valid():
            user = get_user_model().objects.filter(email=form.cleaned_data['email']).first()

            if user:
                #We send email only iff such user exists in the db

                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)

                domain = 'http://' + get_current_site(request).domain
                link = domain + \
                       reverse('user:password-reset-confirm',
                                       kwargs={'uidb64': uid, 'token': token})

                # Send the email to user
                send_mail('InnoRussian: Reset your password',
                          f'Hey!\nWe are ready to reset the password, use your link below:\n{link}',
                          'vladislav.mcfly@yandex.ru',
                          [user.email],
                          fail_silently=False,)

            messages.success(request, 'We sent the link to reset your password :)')

        return redirect('user:sign-in')

    # The user must be not authorized to access this view
    @method_decorator(default_not_authorized)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)




class PasswordResetConfirmView(View):
    """
        View to set new password for the account.
        Using default implementation provided by django.
    """

    def get(self, request, uidb64, token):
        if not self._validate_data(request, uidb64, token):
            return redirect('users:password-reset')

        form = PasswordResentConfirmForm()
        return render(request, 'users/reset_password_change_password.html', context={'form': form})

    def post(self, request, uidb64, token):
        if not self._validate_data(request, uidb64, token):
            return redirect('users:password-reset')

        form = PasswordResentConfirmForm(request.POST)

        if form.is_valid():
            user_id = force_text(urlsafe_base64_decode(uidb64))
            user = form.save(commit=False, pk=user_id)

            try:
                validate_password(form.cleaned_data['password'], user)
            except (ValidationError, ValueError) as e:
                form.add_error('password', e)
            else:
                form.save(commit=True, pk=user.id)
                messages.success(request, 'Your password was successfully updated!')

                user = authenticate(request, username=user.email,
                                    password=form.cleaned_data['password'])
                if user:
                    login(request, user)
                else:
                    messages.warning(request, 'Unknown error occurred during changing the password.'
                                              '\nPlease, try again.')
                    return redirect('users:password-reset')

                return redirect('/')

        return render(request, 'users/reset_password_change_password.html', context={'form': form})

    def _check_uidb64_and_token(self, uidb64, token):
        try:
            user_id = force_text(urlsafe_base64_decode(uidb64))
            user = get_user_model().objects.filter(pk=user_id).first()

            if not user:
                return False
            if not default_token_generator.check_token(user, token):
                return False

            return True
        except Exception as e:
            return False

    # Check that the link is worthy
    def _validate_data(self, request, uidb64, token):
        if not self._check_uidb64_and_token(uidb64, token):
            messages.error(request, 'Invalid link. Please, reset your password again in the form below :)')
            return False
        return True

    # The user must be not authorized to access this view
    @method_decorator(default_not_authorized)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


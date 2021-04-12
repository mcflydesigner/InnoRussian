from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django import forms
from django.utils.translation import gettext_lazy as _
from django.forms import TextInput, PasswordInput, EmailInput
from django.contrib.auth import get_user_model

from .models import CustomUser


class UserSignInForm(forms.Form):
    """ Login form for the custom user model. """

    email = forms.EmailField(widget=TextInput(
                            attrs={'class': 'input100', 'placeholder': _('Enter your email...')}))
    password = forms.CharField(widget=PasswordInput(
                               attrs={'class': 'input100', 'placeholder': _('Enter your password...')}))


class UserSignUpForm(forms.ModelForm):
    """ Registration form for the custom user model. """

    class Meta:
        model = CustomUser
        fields = ('email', 'password', )
        widgets = {
            'email': EmailInput(attrs={'class': 'input100',
                                       'placeholder': _('Enter your email...')}),
            'password': PasswordInput(attrs={'class': 'input100',
                                              'placeholder': _('Enter your password...')}),
        }
        help_texts = {
            'password': 'At least 8 characters'
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user




class PasswordResetForm(forms.Form):
    """
        Reset password form for the custom user model.
        Using this form we send to user's email the letter
        which contains the link to reset their password.
    """

    email = forms.EmailField(widget=EmailInput(attrs={'class': 'input100',
                                                      'placeholder': _('Enter your email...')}))

    def save(self):
        pass



class PasswordResentConfirmForm(forms.ModelForm):
    """
        Confirmation of resetting password form for the custom user model.
        When the user clicks on the reset link, they will enter new password.
    """

    class Meta:
        model = CustomUser
        fields = ('password', )
        widgets = {
            'password': PasswordInput(attrs={'class': 'input100',
                                             'placeholder': _('Enter your password...')}),
        }
        help_texts = {
            'password': 'At least 8 characters'
        }


    def save(self, commit=True, pk=None):
        if not pk:
            raise ValueError(f'Argument pk must be provided')
        user = get_user_model().objects.get(pk=pk)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user





### ADMIN PANEL
class UserCreationForm(UserCreationForm):
    """ Create account form for the custom user model. """

    class Meta:
        model = CustomUser
        fields = ('email', )



class UserChangeForm(UserChangeForm):
    """ Edit account form for the custom user model. """

    class Meta:
        model = CustomUser
        exclude = ('password',)

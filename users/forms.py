from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import password_validation
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.forms import ModelForm

from users.models import Profile


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'имя'
        })
    )
    password = forms.CharField(
        max_length=128,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'пароль'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'password']




class RegistrationForm(UserCreationForm):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'input-box',
            'style': 'padding-left:1rem',
            'placeholder': 'имя'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'input-box',
            'style': 'padding-left:1rem',
            'placeholder': 'email'
        })
    )
    password1 = forms.CharField(
        max_length=128,

        widget=forms.PasswordInput(attrs={
            'class': 'input-box',
            'style': 'padding-left:1rem',
            'placeholder': 'пароль'
        })
    )
    password2 = forms.CharField(
        max_length=128,
        widget=forms.PasswordInput(attrs={
            'class': 'input-box',
            'style': 'padding-left:1rem',
            'placeholder': 'повторите пароль'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', ]




class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label="Email",
        max_length=254,
        widget=forms.EmailInput(
            attrs={'class': 'form-control',
                   'placeholder': 'Введите Email',
                   "autocomplete": "email"}
        )
    )


class ProfileForm(forms.ModelForm):

    username = forms.CharField(

        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'edit-form',
            'style': 'padding-left:1rem',
            'placeholder': 'имя'
        })
    )
    email = forms.EmailField(

        max_length=254,
        widget=forms.EmailInput(
            attrs={'class': 'edit-form',
                   'placeholder': 'email',
                   'style':'padding-left:1rem',
                   "autocomplete": "email"}
        )
    )

    class Meta:
        model = User
        fields = ['username', 'email']




class CustomSetPasswordForm(SetPasswordForm):
    error_messages = {
        "password_mismatch": "Пароли не совпадают"
    }
    new_password1 = forms.CharField(
        label='Новый пароль',
        widget=forms.PasswordInput(
            attrs={'class': 'form-control',
                   'placeholder': 'Введите новый пароль',
                   "autocomplete": "new-password"}
        ),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
    )
    new_password2 = forms.CharField(
        label='Подтверждение нового пароля',
        strip=False,
        widget=forms.PasswordInput(
            attrs={'class': 'form-control',
                   'placeholder': 'Подтвердите новый пароль',
                   "autocomplete": "new-password"}
        ),
    )

from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
#from captcha.fields import ReCaptchaField
from django import forms

# If you don't do this you cannot use Bootstrap CSS
class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Username", max_length=30, 
            widget=forms.TextInput(attrs={'class': 'form-control', 'name': 'username'}))
    password = forms.CharField(label="Password", max_length=30, 
            widget=forms.TextInput(attrs={'class': 'form-control', 'name': 'password'}))


class RegisterForm(UserCreationForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'E-Mail'}), required=True)
    # captcha = ReCaptchaField(attrs={'theme': 'blackglass'})
    password1 = forms.CharField(label="Password",
                                widget=forms.PasswordInput(attrs={"placeholder": "Password"}))
    password2 = forms.CharField(label="Confirm Password",
                                widget=forms.PasswordInput(attrs={'placeholder': 'Verify Password'}))

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name")
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'User Name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'E-Mail'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Last Name'}),
        }
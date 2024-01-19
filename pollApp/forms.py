from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ModelForm, TextInput, NumberInput, PasswordInput


class RegistrationForm(UserCreationForm):
    username = forms.CharField(max_length=30, label='Username', widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ("username", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['password1'].widget = PasswordInput(attrs={'class': 'form-control'})
        self.fields['password2'].widget = PasswordInput(attrs={'class': 'form-control'})


class LoginForm(forms.Form):
    username = forms.CharField(max_length=30, label='Username', widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

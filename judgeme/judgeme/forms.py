# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ObjectDoesNotExist


from .models import JMUser


class JMUserCreationForm(UserCreationForm):

    class Meta:
        model = JMUser
        fields = ("username", "email")


class JMUserChangeForm(UserChangeForm):

    class Meta:
        model = JMUser
        fields = ("username", "email")

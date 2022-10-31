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


class AddFriend(forms.Form):
    username = forms.CharField(label='Add a friend:', max_length=100)

    def get_user_with_username(username) -> JMUser:
        user = None
        try:
            user = JMUser.objects.get(username=username)
            return user
        except ObjectDoesNotExist:
            return None

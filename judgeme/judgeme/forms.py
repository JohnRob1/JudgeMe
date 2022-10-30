from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import JMUser


class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = JMUser
        fields = ('username',)


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = JMUser
        fields = ('username',)

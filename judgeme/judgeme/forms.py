# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ObjectDoesNotExist
from .models import Test, Image, JMUser


from .models import JMUser


class ImageForm(forms.ModelForm):
    #store_image = forms.ImageField()
    class Meta:
        model=Image
        store_image = forms.ImageField()
        fields=("image",)


class uploadedImage(forms.ModelForm):
    #uploadedImage = forms.ImageField()
    class Meta:
        model = JMUser
        fields = ("uploaded_image",
        )

class JMUserCreationForm(UserCreationForm):
    class Meta:
        model = JMUser
        fields = ("username", "email")


class JMUserChangeForm(UserChangeForm):

    class Meta:
        model = JMUser
        fields = ("username", "email")

# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ObjectDoesNotExist
from .models import Test, Image, JMUser


from .models import JMUser


class ImageForm(forms.ModelForm):
    class Meta:
        model=Image
        fields=("image",)

"""
class uploadedImage(forms.ModelForm):
    class Meta:
        model = JMUser
        fields = ("profile_picture", 
        "display_name", 
        "top_tracks", 
        "top_artists",
        "playlist_count",
        "friends",
        "about",
        "vibes", 
        "uploaded_image",
        "music_taste",)"""

class JMUserCreationForm(UserCreationForm):
    class Meta:
        model = JMUser
        fields = ("username", "email")


class JMUserChangeForm(UserChangeForm):

    class Meta:
        model = JMUser
        fields = ("username", "email")

from django.urls import path

from . import views


# from .views import AuthURL, spotify_callback, IsAuthenticated

urlpatterns = [
    path('', views.index),
]

"""judgeme URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path

from . import views
from . import spotify_views
from . import spotipy_test

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('judge/', views.judge, name='judge'),
    path('tutorial/', views.tutorial, name='tutorial'),
    path('spotify/sign-in/', views.sign_in),
    path('judge/', views.judge, name='judge'),
<<<<<<< HEAD
    path('judge/result/', views.result, name='result'),
=======
    path('judge/gif/', views.gif, name='gif'),
>>>>>>> faf81867 (got 3/4 acceptance criteria for gif user story)
    path('profile/', views.profile, name='profile'),
    path('playlist/', views.playlist, name='playlist'),
    path('judge/bar/', views.bar, name='bar'),
    path('judge/graph/', views.graph, name='graph'),
    path('artist/', views.artist, name='artist'),
    path('test/', views.test, name='test'),
    path('spotify-test/', spotipy_test.test, name='test'),
    # path('spotify/sign-in/', views.sign_in),
    # path('', include('login.urls')),
    # path('spotify/', include('spotify.urls')),
    # path('theme/', include('theme.urls')),
    # path('judge/', include('judge.urls')),
    path("__reload__/", include("django_browser_reload.urls")),
]

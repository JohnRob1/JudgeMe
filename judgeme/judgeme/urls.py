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

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('tutorial/', views.tutorial, name='tutorial'),
    path('spotify/sign-in/', spotify_views.sign_in),
    # path('spotify/sign-in/', views.sign_in),
    # path('', include('login.urls')),
    # path('spotify/', include('spotify.urls')),
    # path('theme/', include('theme.urls')),
    # path('judge/', include('judge.urls')),
    path("__reload__/", include("django_browser_reload.urls")),
]
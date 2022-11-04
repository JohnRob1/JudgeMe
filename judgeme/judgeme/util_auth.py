
from __future__ import print_function
import spotipy.oauth2 as oauth2
import spotipy
from ast import literal_eval

from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate, login

from .models import JMUser

SPOTIPY_CLIENT_ID = '1fba4b0df2fe49318273c0ab3aeb1d49'
SPOTIPY_CLIENT_SECRET = '8d0bfdb045024e74bbdc22cd47c69588'
SPOTIPY_REDIRECT_URI = 'http://127.0.0.1:8000/callback/'
# https://developer.spotify.com/documentation/general/guides/authorization/scopes/ for scopes
SPOTIFY_SCOPE = 'user-top-read user-library-read playlist-read-private playlist-modify-public user-read-private user-read-email user-read-recently-played'
username = ''


def generate_url(show_dialog=True):

    sp_oauth = oauth2.SpotifyOAuth(
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET,
        redirect_uri=SPOTIPY_REDIRECT_URI,
        scope=SPOTIFY_SCOPE,
        show_dialog=show_dialog
    )

    auth_url = sp_oauth.get_authorize_url()
    return auth_url


def create_token_info(code, show_dialog=False):
    print("Creating token")

    sp_oauth = oauth2.SpotifyOAuth(
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET,
        redirect_uri=SPOTIPY_REDIRECT_URI,
        scope=SPOTIFY_SCOPE,
        show_dialog=show_dialog
    )

    if code:
        token_info = sp_oauth.get_access_token(code=code, check_cache=False)
    else:
        return None

    if token_info:
        return token_info
    else:
        return None


def check_token(token_info):
    token_info = literal_eval(token_info)
    sp_oauth = oauth2.SpotifyOAuth(
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET,
        redirect_uri=SPOTIPY_REDIRECT_URI,
        scope=SPOTIFY_SCOPE,
    )
    if sp_oauth.is_token_expired(token_info):
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])

    return token_info


def login_django_user(request):

    sp_oauth = oauth2.SpotifyOAuth(
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET,
        redirect_uri=SPOTIPY_REDIRECT_URI,
        scope=SPOTIFY_SCOPE,
    )
    sp: spotipy.Spotify = spotipy.Spotify(
        auth_manager=sp_oauth)

    sp_user = sp.me()
    sp_id = sp_user.get("id")
    sp_email = sp_user.get("email")
    images = sp_user.get("images")
    if len(images) == 0:
        sp_profile_picture = "https://static.vecteezy.com/system/resources/thumbnails/005/544/770/small/profile-icon-design-free-vector.jpg"
    else:
        sp_profile_picture = images[0].get("url")

    user = None
    try:
        user = JMUser.objects.get(username=sp_id)
    except ObjectDoesNotExist:
        user = JMUser.objects.create_user(sp_id, sp_email, 'password')
        user.profile_picture = sp_profile_picture
        user.is_superuser = True
        user.is_staff = True
        user.save()
        print("user created.")

    login(request, user)

from pprint import pprint
from pydoc import cli
from typing import Dict
from urllib.request import HTTPRedirectHandler
from django.shortcuts import render, HttpResponseRedirect
from django.contrib.auth import authenticate, login
from django.core.exceptions import ObjectDoesNotExist
from django.urls import is_valid_path
from . import spotify_views
from .forms import AddFriend

# from django.contrib.auth.models import User
from .models import JMUser

import spotipy
import os
from spotipy import oauth2
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth

SPOTIPY_CLIENT_ID = '1fba4b0df2fe49318273c0ab3aeb1d49'
SPOTIPY_CLIENT_SECRET = '8d0bfdb045024e74bbdc22cd47c69588'
SPOTIPY_REDIRECT_URI = 'http://127.0.0.1:8000/tutorial/'
# https://developer.spotify.com/documentation/general/guides/authorization/scopes/ for scopes
scope = 'user-top-read user-library-read playlist-read-private playlist-modify-public user-read-private user-read-email'
username = ''


def sign_in(request):
    # token = util.prompt_for_user_token(username, scope)
    # print(token)
    print("signing in ")
    sp_oauth = oauth2.SpotifyOAuth(
        SPOTIPY_CLIENT_ID,
        SPOTIPY_CLIENT_SECRET,
        SPOTIPY_REDIRECT_URI,
        scope=scope,
        cache_path=".cache-" + username)

    token_info = sp_oauth.get_cached_token()
    if not token_info:
        print("No token?")
        auth_url = sp_oauth.get_authorize_url()
        return HttpResponseRedirect(auth_url)

    return render(request, 'tutorial.html')


def index(request):
    return render(request, 'index.html')


def about(request):
    return render(request, 'about.html')


def spotify(request):
    return render(request, 'spotify.html')


def tutorial(request):
    return render(request, 'tutorial.html')


def judge(request):
    return render(request, 'judge.html')


def profile(request):
    return render(request, 'profile.html')


def playlist(request):
    return render(request, 'playlist.html')


def bar(request):
    return render(request, 'bar.html')


def graph(request):
    return render(request, 'graph.html')


def artist(request):
    return render(request, 'artist.html')


def base(request):
    return render(request, 'base.html')


def login_user(request):

    os.environ['SPOTIPY_CLIENT_ID'] = SPOTIPY_CLIENT_ID
    os.environ['SPOTIPY_CLIENT_SECRET'] = SPOTIPY_CLIENT_SECRET
    os.environ['SPOTIPY_REDIRECT_URI'] = SPOTIPY_REDIRECT_URI

    scope = "user-library-read user-top-read"

    sp: spotipy.Spotify = spotipy.Spotify(
        auth_manager=SpotifyOAuth(scope=scope))

    sp_user = sp.me()
    sp_id = sp_user.get("id")
    sp_email = sp_user.get("email")
    sp_profile_picture = sp_user.get("images")[0].get("url")

    user = None
    try:
        user = JMUser.objects.get(username=sp_id)
    except ObjectDoesNotExist:
        user = JMUser.objects.create_user(sp_id, sp_email, 'password')
        user.profile_picture = sp_profile_picture
        user.save()
        print("user created.")

    login(request, user)

    context = {}
    context['user'] = request.user
    context['friends'] = request.user.friends.all()

    # return HttpResponseRedirect('/home/')
    return render(request, 'friends.html', context)


def update_top_tracks():

    pass


def find_friend(request):
    if request.method == 'POST':
        form = AddFriend(request.POST)
        if form.is_valid():

            return HttpResponseRedirect('/friends/')
    else:
        form = AddFriend()

    return render(request, 'friends.html', {'form': form})


def friends(request):
    context = {}
    context['user'] = request.user
    context['friends'] = request.user.friends.all()
    return render(request, 'friends.html', context)
    # return render(request, 'friend_listing.html')


def test(request):
    os.environ['SPOTIPY_CLIENT_ID'] = SPOTIPY_CLIENT_ID
    os.environ['SPOTIPY_CLIENT_SECRET'] = SPOTIPY_CLIENT_SECRET
    os.environ['SPOTIPY_REDIRECT_URI'] = SPOTIPY_REDIRECT_URI

    scope = "user-library-read user-top-read"

    sp: spotipy.Spotify = spotipy.Spotify(
        auth_manager=SpotifyOAuth(scope=scope))

    aaa = sp.current_user_top_tracks(2)
    pprint(aaa)

    # features = sp.audio_features(urn)
    # # Array index 0 because we're only passing in one urn. This is a dictionary.
    # features_dict = features[0]
    # for key, value in features_dict.items():
    #     print(key, ": ", value)

    # tracks = sp.curr

    # profile = sp.current_user()
    # for key, value in profile.items():
    #     print(key, ": ", value)

    # print(features)

    # user = sp.user("virtualkenny")
    # pprint(user)

    # for key, value in track.items():
    #     print(key, ": ", value)

    return render(request, 'index.html')


def get_spotify_object_old() -> spotipy.Spotify:
    client_credentials_manager = SpotifyClientCredentials(
        SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    # sp = spotipy.Spotify(auth_manager=spotipy.SpotifyOAuth(
    #     client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET, redirect_uri=SPOTIPY_REDIRECT_URI, scope=scope))
    return sp


def get_spotify_object() -> spotipy.Spotify:
    os.environ['SPOTIPY_CLIENT_ID'] = SPOTIPY_CLIENT_ID
    os.environ['SPOTIPY_CLIENT_SECRET'] = SPOTIPY_CLIENT_SECRET
    os.environ['SPOTIPY_REDIRECT_URI'] = SPOTIPY_REDIRECT_URI

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

    return sp

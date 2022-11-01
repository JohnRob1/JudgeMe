from multiprocessing import context
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
import random

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

def result(request):
    # Implement Comparison Algorithm
    # os.environ['SPOTIPY_CLIENT_ID'] = SPOTIPY_CLIENT_ID
    # os.environ['SPOTIPY_CLIENT_SECRET'] = SPOTIPY_CLIENT_SECRET
    # os.environ['SPOTIPY_REDIRECT_URI'] = SPOTIPY_REDIRECT_URI

    # scope = "user-library-read user-top-read"

    # sp: spotipy.Spotify = spotipy.Spotify(
    #     auth_manager=SpotifyOAuth(scope=scope))

    # topHunna = sp.current_user_top_tracks(100, 0, "medium_term")
    # for track in topHunna['items']:
    #     print(track)


    f = open('theme/static/light_mode_gifs/insults.txt', 'r')
    lines = f.readlines()
    r = random.randint(0, len(lines) - 1)

    context = {
        'gif' : lines[r].format,
    }
    return render(request, 'result.html', context)

def profile(request):
    return render(request, 'profile.html')


def playlist(request):
    return render(request, 'playlist.html')


def bar(request):
    return render(request, 'bar.html')


def graph(request):
    return render(request, 'graph.html')


def artist(request):
    sp: spotipy.Spotify = get_spotify_object()
    print(sp)

    artist = '  '
    if 'aname' in request.POST:
        artist = request.POST['aname']
        if 'aname' in request.POST:
            result = sp.search(q=artist, limit=1, type='artist')
            for i,t in enumerate(result['artists']['items']):
                name = t['name']
                print(name)
                artistId = t['id']
                uri = t['uri']

                holder = []
                top_tracks = sp.artist_top_tracks(uri)
                for track in top_tracks['tracks'][:5]:
                    print('track    : ' + track['name'])
                    print()
                    holder.append(track['name'])
                
                
                results = sp.artist_albums(uri, album_type='album')
                albums = results['items']
                while results['next']:
                    results = spotify.next(results)
                    albums.extend(results['items'])

                album_titles = []

                for album in albums:
                    album_titles.append(album['name'])
                
                print(album_titles)

                context = {
                    'render_intro' : False,
                    'top_tracks' : holder,
                    'album_titles' : album_titles,
                }
                return render(request, 'artist.html', context)
            return render(request, 'artist.html', {'error': True})
    context = {
        'render_intro' : True,
        'dontrun': True,
    }

    return render(request, 'artist.html', context)

def breakdown(request):

    sp: spotipy.Spotify = get_spotify_object()
    print(sp)

    # ranges = ['short_term', 'medium_term', 'long_term']
    ranges = ['medium_term']
    top_song_ids = []
    all_artists = []
    all_genres = []

    for sp_range in ranges:
        print("range:", sp_range)
        results = sp.current_user_top_tracks(time_range=sp_range, limit=50)
        for i, item in enumerate(results['items']):
            #print(i, item['name'], '//', item['artists'][0]['name'])
            top_song_ids.append(item['id'])
            all_artists.append(item['artists'][0]['name'])
            album = sp.album(item["album"]["external_urls"]["spotify"])
            all_genres.append(album["genres"])
            print(album["genres"])
            print()
        print()

    
    print(all_artists)
    print()
    print(all_genres)
    print()
    print(top_song_ids)
    return render(request, 'breakdown.html')


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

    if 'add-friend' in request.GET:
        username = request.GET['add-friend']
        print("trying to add:", username)

        try:

            user = JMUser.objects.get(username=username)
            request.user.friends.add(user)
            print("friend added.")
        except ObjectDoesNotExist:
            print("doesn't exist!!")
            pass

    if 'remove-friend' in request.GET:
        username = request.GET['remove-friend']
        print("trying to remove:", username)
        try:
            user = JMUser.objects.get(username=username)
            request.user.friends.remove(user)
            print("friend removed.")
        except ObjectDoesNotExist:
            print("doesn't exist!!")

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
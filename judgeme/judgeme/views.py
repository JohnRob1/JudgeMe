from distutils.log import debug
from pprint import pprint
from urllib.request import HTTPRedirectHandler
from django.shortcuts import render, HttpResponseRedirect, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.urls import is_valid_path

from .util_auth import generate_url, create_token_info, check_token, login_django_user

from .models import JMUser, Track

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
darkmode = False


def sign_in(request):
    url = generate_url()
    return HttpResponseRedirect(url)


def spotify_callback(request):
    if request.GET.get('error'):
        # User pressed cancel
        return redirect('..')

    code = request.GET.get('code')
    token = create_token(code)

    request.session['code'] = code
    request.session['token'] = token
    request.session.set_expiry(0)

    return redirect('login')


def create_token(code):
    token_info = create_token_info(code=code)
    if token_info == None:
        return None

    return token_info['access_token']


def get_spotify_object(request) -> spotipy.Spotify:
    token = request.session.get('token')
    if token == None:
        code = request.session.get('code')
        create_token(code)

    return spotipy.Spotify(auth=token)


def index(request):
    context = {}
    context["bg_color"] = "white"
    context["bubble_color"] = "black/30"
    return render(request, 'index.html', context)


def about(request):
    context = {}
    context["bg_color"] = "[#355e3b]"
    context["bubble_color"] = "[#518634]"
    return render(request, 'about.html', context)


def spotify(request):
    return render(request, 'spotify.html')


def welcome(request):
    context = {}
    context["bg_color"] = "[#322c3d]"
    context["bubble_color"] = "[#8e3d81]"
    return render(request, 'tutorial.html', context)


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

def tutorial(request):
    return render(request, 'tutorial.html')


def homepage(request):
    sp = get_spotify_object(request)
    iterations = 0
    playlists = []
    while(True):
        result = sp.current_user_playlists(limit=50, offset=iterations*50)
        items = result.get('items')
        if (len(items) == 0):
            break
        iterations += 1
        for playlist in items:
            playlists.append(playlist)
    

    count = 0
    for item in playlists:
        if item.get('owner').get('id') == request.user.username:
            count += 1
            
    context = {'user':request.user, 'friendcount':request.user.friends.count(), 'playlist_count':count}
    return render(request, 'homepage.html', context)

def profiledit(request):
    return render(request, 'profiledit.html')

def temp(request):
    return render(request, 'temp.html')

def artist(request):
    return render(request, 'artist.html')

def generate(request):
    if 'next' in request.GET:
        print("hi")

    if 'darkMode' in request.GET:
        darkmode = True

    if 'lightMode' in request.GET:
        darkmode = False

    return render(request, 'generate.html')

def artist(request):
    sp: spotipy.Spotify = get_spotify_object(request)
    print(sp)

    artist = '  '
    if 'aname' in request.POST:
        artist = request.POST['aname']
        if 'aname' in request.POST:
            result = sp.search(q=artist, limit=1, type='artist')
            for i, t in enumerate(result['artists']['items']):
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
                    'render_intro': False,
                    'top_tracks': holder,
                    'album_titles': album_titles,
                }
                return render(request, 'artist.html', context)
            return render(request, 'artist.html', {'error': True})
    context = {
        'render_intro': True,
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

    login_django_user(request)

    context = {}
    context['user'] = request.user
    context['friends'] = request.user.friends.all()

    return redirect('welcome')
    # return render(request, "friends.html")


def update_top_tracks(request):
    request.user.top_tracks.clear()

    sp = get_spotify_object(request)
    for track in sp.current_user_top_tracks(50).get("items"):
        song_uri = track.get("uri")
        track = get_or_create_track_from_uri(request, song_uri)
        request.user.top_tracks.add(track)


def get_or_create_track_from_uri(request, uri) -> Track:
    sp = get_spotify_object(request)
    name = sp.track(uri).get("name")
    track, created = Track.objects.get_or_create(uri=uri, name=name)
    print(track)
    return track


def friends(request):
    context = {}
    context['user'] = request.user
    context['friends'] = request.user.friends.all()
    context["bg_color"] = "[#322c3d]"
    context["bubble_color"] = "[#8e3d81]"

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


def print_top_genres(request):
    sp = get_spotify_object(request)
    for track in sp.current_user_top_tracks(10).get("items"):
        song_uri = track.get("uri")
        artist_id = sp.track(song_uri).get("artists")[0].get("id")
        artist = sp.artist(artist_id)
        genres = artist.get("genres")
        top_genre = genres[0]
        pprint(top_genre)


def test(request):

    return render(request, 'test.html')

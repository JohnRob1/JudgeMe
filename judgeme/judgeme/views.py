from distutils.log import debug
from pprint import pprint
from urllib.request import HTTPRedirectHandler
from django.shortcuts import render, HttpResponseRedirect, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.urls import is_valid_path
from . import spotify_views
from .forms import AddFriend
import random

from .util_auth import generate_url, create_token_info, check_token, login_django_user

from .models import JMUser, Track

import spotipy
import os


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
    return render(request, 'index.html')


def about(request):
    return render(request, 'about.html')


def spotify(request):
    return render(request, 'spotify.html')


def welcome(request):
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

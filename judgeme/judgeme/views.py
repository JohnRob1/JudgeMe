from pprint import pprint
from urllib.request import HTTPRedirectHandler
from django.shortcuts import render, HttpResponseRedirect, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.urls import is_valid_path

from .util_auth import generate_url, create_token, check_token, login_django_user

from .models import JMUser

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

    token_info = create_token(code=code)

    token = token_info['access_token']
    request.session['token'] = token

    return redirect('login')


def get_sp(request) -> spotipy.Spotify:
    token = request.session.get('token')
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

    login_django_user(request)
    # for track in sp.current_user_top_tracks(1):
    #     pprint(track)

    # song_uri = "spotify:track:7lEptt4wbM0yJTvSG5EBof"
    # artist_id = sp.track(song_uri).get("artists")[0].get("id")
    # artist = sp.artist(artist_id)
    # genres = artist.get("genres")
    # pprint(genres)

    context = {}
    context['user'] = request.user
    context['friends'] = request.user.friends.all()

    return redirect('welcome')
    # return render(request, "friends.html")


def update_top_tracks():

    pass


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

    return render(request, 'test.html')

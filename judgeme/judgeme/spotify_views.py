from django.shortcuts import render, redirect, HttpResponseRedirect

import requests
import spotipy
import spotipy.util as util
from spotipy import oauth2

SPOTIPY_CLIENT_ID = '1fba4b0df2fe49318273c0ab3aeb1d49'
SPOTIPY_CLIENT_SECRET = '8d0bfdb045024e74bbdc22cd47c69588'
SPOTIPY_REDIRECT_URI = 'http://127.0.0.1:8000/tutorial/'
# https://developer.spotify.com/documentation/general/guides/authorization/scopes/ for scopes
scope = 'user-top-read user-library-read playlist-read-private playlist-modify-public'
username = ''

sp: spotipy.Spotify = None


def next_offset(n):
    try:
        return int(n['next'].split('?')[1].split('&')[0].split('=')[1])
    except ValueError:
        return None
    except AttributeError:
        return None
    except TypeError:
        return None


def sign_in(request):
    # token = util.prompt_for_user_token(username, scope)
    # print(token)
    sp_oauth = oauth2.SpotifyOAuth(
        SPOTIPY_CLIENT_ID,
        SPOTIPY_CLIENT_SECRET,
        SPOTIPY_REDIRECT_URI,
        scope=scope,
        cache_path=".cache-" + username)

    token_info = sp_oauth.get_cached_token()
    if not token_info:
        auth_url = sp_oauth.get_authorize_url()
        return HttpResponseRedirect(auth_url)
    sp = spotipy.Spotify(auth=token_info['access_token'])
    total = []
    results = sp.current_user_saved_tracks(limit=50)
    next = next_offset(results)

    total.append(results)
    while next and next < int(results['total']):
        next_50 = sp.current_user_saved_tracks(limit=50, offset=next)
        next = next_offset(next_50)
        total.append(next_50)
        print(next)
    tracks = []
    for r in total:
        for track in r['items']:
            tracks.append(track)

    return render(request, 'pages/sign-in.html', {'results': tracks})


def get_spotify_object() -> spotipy.Spotify:
    # token = util.prompt_for_user_token(username, scope)
    # print(token)
    sp_oauth = oauth2.SpotifyOAuth(
        SPOTIPY_CLIENT_ID,
        SPOTIPY_CLIENT_SECRET,
        SPOTIPY_REDIRECT_URI,
        scope=scope,
        cache_path=".cache-" + username)

    token_info = sp_oauth.get_cached_token()
    if not token_info:
        auth_url = sp_oauth.get_authorize_url()
        return HttpResponseRedirect(auth_url)
    sp = spotipy.Spotify(auth=token_info['access_token'])
    return sp

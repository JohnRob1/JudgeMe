from django.shortcuts import render, redirect, HttpResponseRedirect

import os
import sys
import time
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth


def test(request):
    os.environ['SPOTIPY_CLIENT_ID'] = '1fba4b0df2fe49318273c0ab3aeb1d49'
    os.environ['SPOTIPY_CLIENT_SECRET'] = '8d0bfdb045024e74bbdc22cd47c69588'
    os.environ['SPOTIPY_REDIRECT_URI'] = 'http://127.0.0.1:8001/tutorial/'

    scope = "user-library-read"

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

    # results = sp.current_user_saved_tracks()
    # for idx, item in enumerate(results['items']):
    #     track = item['track']
    #     print(idx, track['artists'][0]['name'], " – ", track['name'])

    # sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

    urn = 'spotify:track:0Svkvt5I79wficMFgaqEQJ'

    track = sp.track(urn)
    print(track)

    # start = time.time()
    # analysis = sp.audio_analysis(urn)
    # delta = time.time() - start
    # print(json.dumps(analysis, indent=4))
    # print("analysis retrieved in %.2f seconds" % (delta,))

    return render(request, 'index.html')

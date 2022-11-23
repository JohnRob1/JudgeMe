from django.shortcuts import render, HttpResponseRedirect, redirect

from .util_auth import get_spotify_object

def audio_test(request):
    sp = get_spotify_object(request)

    context = {}
    song_uri = request.user.top_tracks.all()[0].uri
    song = sp.track(song_uri)
    url = song.get("preview_url")
    print(url)
    context["url"] = url
    return render(request, 'audio_preview_test.html', context)


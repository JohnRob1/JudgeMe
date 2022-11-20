from pprint import pprint

from .util_auth import get_spotify_object
from .models import Track, Artist


def get_num_friends(request, user) -> int:
    return len(user.friends.all())


def get_user_playlists(request):
    sp = get_spotify_object(request)

    all_playlists = []
    iterations = 0
    while (True):
        result = sp.current_user_playlists(limit=50, offset=iterations*50)
        items = result.get('items')
        if (len(items) == 0):
            break
        iterations += 1
        for playlist in items:
            all_playlists.append(playlist)

    user_playlists = []
    for item in all_playlists:
        if item.get('owner').get('id') == request.user.username:
            user_playlists.append(item)

    return user_playlists


def get_num_playlists(request, user) -> int:
    if user.playlist_count == -1:
        user.playlist_count = len(get_user_playlists(request))
        user.save()
        print("Calculated playlists")

    return user.playlist_count


def get_or_create_track_from_uri(request, uri) -> Track:
    # If the track exists, return it.
    track = Track.objects.filter(uri=uri).first()
    if track != None:
        return track

    sp = get_spotify_object(request)

    # If no track exists with this uri, return None.
    track = sp.track(uri)
    if track == None:
        return None

    name = track.get("name")
    artist_name = track.get("artists")[0].get("name")
    images = track.get("album").get("images")
    picture = images[0].get("url") if images != None else "None"
    track, created = Track.objects.get_or_create(
        uri=uri, name=name, artist_name=artist_name, picture=picture)
    return track


def get_or_create_artist_from_uri(request, uri) -> Artist:
    # If the artist exists, return it.
    artist = Artist.objects.filter(uri=uri).first()
    if artist != None:
        return artist

    sp = get_spotify_object(request)
    artist = sp.artist(uri)
    if artist == None:
        return None

    name = artist.get("name")
    picture = artist.get("images")[0]
    genre = None
    genres = artist.get("genres")
    if len(genres) > 0:
        genre = genres[0]
    artist, created = Artist.objects.get_or_create(
        uri=uri, name=name, picture=picture, top_genre=genre)
    return artist


def update_user_stats(request):
    request.user.top_tracks.clear()
    request.user.top_artists.clear()

    sp = get_spotify_object(request)
    for track in sp.current_user_top_tracks(10).get("items"):
        song_uri = track.get("uri")
        track = get_or_create_track_from_uri(request, song_uri)
        request.user.top_tracks.add(track)

    for artist in sp.current_user_top_artists(10).get("items"):
        artist_uri = artist.get("uri")
        artist = get_or_create_artist_from_uri(request, artist_uri)
        request.user.top_artists.add(artist)

    request.user.save()


def get_top_song(request, user):
    sp = get_spotify_object(request)
    songs = user.top_tracks.all()
    if len(songs) == 0:
        return "No user data"

    return songs[0].name


def get_top_artist(request, user):
    sp = get_spotify_object(request)
    artists = user.top_artists.all()
    if len(artists) == 0:
        return "No user data"

    return artists.all()[0].name


def get_top_genre(request, user):
    sp = get_spotify_object(request)
    artists = user.top_artists.all()
    if len(artists) == 0:
        return "No user data"

    genre_dict: dict = {}
    for artist in artists:
        genre = artist.top_genre
        if genre_dict.get(genre) == None:
            genre_dict[genre] = 0
        genre_dict[genre] += 1

    top_genre = None
    highest_num = 0
    for genre in genre_dict.keys():
        if genre_dict[genre] > highest_num:
            top_genre = genre
            highest_num = genre_dict[genre]

    return top_genre.title()

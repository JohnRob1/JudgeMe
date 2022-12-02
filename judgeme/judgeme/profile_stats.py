from pprint import pprint

from .util_auth import get_spotify_object
from .models import Track, Artist, Playlist


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
    if uri == None:
        return

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
    audio_preview = track.get("preview_url")
    if audio_preview == None:
        audio_preview = "None"
    picture = images[0].get("url") if images != None else "None"
    track, created = Track.objects.get_or_create(
        uri=uri, name=name, artist_name=artist_name, picture=picture, audio_preview=audio_preview)
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
    genre = "No genre"
    genres = artist.get("genres")
    if len(genres) > 0:
        genre = genres[0]
    artist, created = Artist.objects.get_or_create(
        uri=uri, name=name, picture=picture, top_genre=genre)
    return artist

def get_or_create_playlist(request, uri) -> Playlist:
    # If the playlist exists, return it.
    playlist = Playlist.objects.filter(uri=uri).first()
    if playlist != None:
        return playlist 

    sp = get_spotify_object(request)
    sp_playlist = sp.playlist(uri)
    if sp_playlist == None:
        return None
    
    name = sp_playlist.get("name")
    if len(sp_playlist.get("images")) > 0:
        picture = sp_playlist.get("images")[0].get("url")
    else:
        picture = "No Data"

    playlist, created = Playlist.objects.get_or_create(
        uri=uri, name=name, playlist_pic=picture)
    
    sp_tracks = sp_playlist.get("tracks").get("items")
    for track in sp_tracks:
        song_uri = track.get("uri")
        track = get_or_create_track_from_uri(request, song_uri)
        playlist.tracks.add(track)
    

    return playlist 

def update_user_stats(request):
    request.user.top_tracks.clear()
    request.user.top_artists.clear()
    request.user.music_taste = -1
    get_music_taste(request, request.user)

    sp = get_spotify_object(request)
    playlists = get_user_playlists(request)
    for playlist in playlists:
        playlist_uri = playlist.get("uri") 
        playlist = get_or_create_playlist(request, playlist_uri)
        request.user.playlists.add(playlist)

    for track in sp.current_user_top_tracks(10).get("items"):
        song_uri = track.get("uri")
        track = get_or_create_track_from_uri(request, song_uri)
        request.user.top_tracks.add(track)

    top_track = request.user.top_tracks.all()[0]
    request.user.top_track_name = top_track.name + " - " + top_track.artist_name

    for artist in sp.current_user_top_artists(10).get("items"):
        artist_uri = artist.get("uri")
        artist = get_or_create_artist_from_uri(request, artist_uri)
        request.user.top_artists.add(artist)

    request.user.save()


def get_top_song(request, user):
    return user.top_track_name
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


def get_music_taste(request, user):
    f = open('theme/static/genre_correlations', 'r')
    glines = f.readlines()
    genres_cf = {}
    genres_amt = {}
    return_dict = {}
    for line in glines:
        values = line.split(",")
        values[5] = values[5].strip()
        genres_cf[values[0].lower()] = values[1:]
    # Get genres of songs for weight
    sp = get_spotify_object(request)
    total_genres = 0
    tracks = user.top_tracks.all()
    for track in tracks:
        song_uri = track.uri
        artist_id = sp.track(song_uri).get("artists")[0].get("id")
        artist = sp.artist(artist_id)
        genres = artist.get("genres")
        for genre in genres:
            added_to_dict = False
            if genres_cf.get(genre, None) != None:
                added_to_dict = True
                if genres_amt.get(genre, None) == None:
                    genres_amt[genre] = 1
                    total_genres = total_genres + 1
                else:
                    genres_amt[genre] = genres_amt.get(genre) + 1
                    total_genres = total_genres + 1
            else:
                # Check is the genre given is just the subtype of a genre in the correlation values
                split = genre.split()
                for word in split:
                    if genres_cf.get(word, None) != None:
                        added_to_dict = True
                        if genres_amt.get(word, None) == None:
                            genres_amt[word] = 1
                            total_genres = total_genres + 1
                        else:
                            genres_amt[word] = genres_amt.get(word) + 1
                            total_genres = total_genres + 1
            # Genre has no personality correlation
            # correlation is [3,3,3,3,3]
            if added_to_dict is False:
                if genres_amt.get(genre, None) == None:
                    genres_amt[genre] = 1
                    total_genres = total_genres + 1
                else:
                    genres_amt[genre] = genres_amt.get(genre) + 1
                    total_genres = total_genres + 1
                genres_cf[genre] = [3, 3, 3, 3, 3]

    # Calculate MusicTaste
    for genre in genres_amt.keys():
        personality_array = genres_cf.get(genre, [3, 3, 3, 3, 3])
        weight = genres_amt.get(genre) / len(genres_amt)
        user.agreeableness = user.agreeableness + \
            (float(personality_array[0]) * weight)
        user.conscientiousness = user.conscientiousness + \
            (float(personality_array[1]) * weight)
        user.emotional_stability = user.emotional_stability + \
            (float(personality_array[2]) * weight)
        user.extravertedness = user.extravertedness + \
            (float(personality_array[3]) * weight)
        user.openness = user.openness + (float(personality_array[4]) * weight)

    value = 0
    if (user.agreeableness < 3):
        return_dict['agreeableness'] = "Not Agreeable"
    else:
        value = value + 51
        return_dict['agreeableness'] = "Agreeable"

    if (user.conscientiousness < 3):
        return_dict['concientiousness'] = "Not Conscientious"
    else:
        value = value + 25
        return_dict['concientiousness'] = "Conscientious"

    if (user.openness < 3):
        return_dict['openness'] = "Not Open"
    else:
        value = value + 12.5
        return_dict['openness'] = "Open"

    if (user.emotional_stability < 3):
        return_dict['emotional_stability'] = "Not Emotionally Stable"
    else:
        value = value + 6.25
        return_dict['emotional_stability'] = "Emotionally Stable"

    if (user.extravertedness < 3):
        return_dict['extraverted'] = "Introverted"
    else:
        value = value + 3.125
        return_dict['extraverted'] = "Extroverted"

    value = value / 3.125
    user.music_taste = int(value) + 1
    user.save()
    return return_dict

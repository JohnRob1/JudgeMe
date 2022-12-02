from distutils.log import debug
from pprint import pprint
from urllib.request import HTTPRedirectHandler
from django.shortcuts import render, HttpResponseRedirect, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.urls import is_valid_path
from django.conf import settings
import random

from .util_auth import generate_url, create_token_info, login_django_user, get_spotify_object
from .profile_stats import get_or_create_track_from_uri

from .models import JMUser, Track
from .profile_stats import update_user_stats, get_top_artist, get_top_genre, get_top_song, get_num_friends, get_num_playlists

import spotipy
import os
import random


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
    print("AWDAA", request.session['token'])

    return redirect('login')


def create_token(code):
    token_info = create_token_info(code=code)
    if token_info == None:
        return None

    return token_info['access_token']


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
    context = {}
    context['friends'] = request.user.friends.all()
    if "friend" in request.GET:
        friend = JMUser.objects.get(username=request.GET.get("friend"))
        return result(request, friend)
    return render(request, 'judge.html', context)


def result(request, friend):

    # Implement Comparison Algorithm
    MusicTaste = 0
    MusicTaste2 = 0

    # Read in Correlation Factors into Hash
    f = open('theme/static/genre_correlations', 'r')
    glines = f.readlines()
    genres_cf = {}
    genres_amt = {}
    for line in glines:
        values = line.split(",")
        values[1] = values[1].strip()
        genres_cf[values[0].lower()] = values[1]
    # Get genres of songs for weight
    sp = get_spotify_object(request)

    for track in friend.top_tracks.all():
        artist_id = sp.track(track).get("artists")[0].get("id")
        artist = sp.artist(artist_id)
        genres = artist.get("genres")
        for genre in genres:
            added_to_dict = False
            if genres_cf.get(genre, None) != None:
                added_to_dict = True
                if genres_amt.get(genre, None) == None:
                    genres_amt[genre] = 0
                else:
                    genres_amt[genre] = genres_amt.get(genre) + 1
            else:
                # Check is the genre given is just the subtype of a genre in the correlation values
                split = genre.split()
                for word in split:
                    if genres_cf.get(word, None) != None:
                        added_to_dict = True
                        if genres_amt.get(word, None) == None:
                            genres_amt[word] = 0
                        else:
                            genres_amt[word] = genres_amt.get(word) + 1
            # Genre has no personality correlation
            # CF = 3/36
            if added_to_dict is False:
                if genres_amt.get(genre, None) == None:
                    genres_amt[genre] = 0
                else:
                    genres_amt[genre] = genres_amt.get(genre) + 1
                genres_cf[genre] = 3/36

    # Calculate MusicTaste
    for genre in genres_amt.keys():
        MusicTaste2 = MusicTaste2 + ((float(genres_amt.get(genre, 0) / 100)) * float(genres_cf.get(genre, 0)))
    friend.music_taste = round(MusicTaste2 * 100, 2)

    for track in sp.current_user_top_tracks(1).get("items"):
        song_uri = track.get("uri")
        artist_id = sp.track(song_uri).get("artists")[0].get("id")
        artist = sp.artist(artist_id)
        print("Working...")
        genres = artist.get("genres")
        for genre in genres:
            added_to_dict = False
            if genres_cf.get(genre, None) != None:
                added_to_dict = True
                if genres_amt.get(genre, None) == None:
                    genres_amt[genre] = 0
                else:
                    genres_amt[genre] = genres_amt.get(genre) + 1
            else:
                # Check is the genre given is just the subtype of a genre in the correlation values
                split = genre.split()
                for word in split:
                    if genres_cf.get(word, None) != None:
                        added_to_dict = True
                        if genres_amt.get(word, None) == None:
                            genres_amt[word] = 0
                        else:
                            genres_amt[word] = genres_amt.get(word) + 1
            # Genre has no personality correlation
            # CF = 3/36
            if added_to_dict is False:
                if genres_amt.get(genre, None) == None:
                    genres_amt[genre] = 0
                else:
                    genres_amt[genre] = genres_amt.get(genre) + 1
                genres_cf[genre] = 3/36

    # Calculate MusicTaste
    for genre in genres_amt.keys():
        MusicTaste = MusicTaste + ((float(genres_amt.get(genre, 0) / 100)) * float(genres_cf.get(genre, 0)))
    request.user.music_taste = round(MusicTaste * 100, 2)

    if abs(request.user.music_taste - friend.music_taste) < 20:
        f = open('theme/static/light_mode_gifs/comps.txt', 'r')
    else:
        f = open('theme/static/light_mode_gifs/insults.txt', 'r')
    lines = f.readlines()
    r = random.randint(0, len(lines) - 1)
    line = lines[r]
    sh = line.split(", ")

    context = {
        'src': sh[0],
        'height': sh[1],
        'href': sh[2].strip("\n"),
        'me_pp': request.user.profile_picture,
        'me_mt': request.user.music_taste,
        'friend_pp': friend.profile_picture,
        'friend_mt': friend.music_taste,
    }
    return render(request, 'result.html', context)


def profile(request):
    sp = get_spotify_object(request)

    user = request.user
    if "user" in request.GET:
        try:
            user = JMUser.objects.get(username=request.GET.get('user'))
        except:
            user = None
            pass

    if "about" in request.GET:
        user.about = request.GET['about']
    if "vibes" in request.GET:
        user.vibes = request.GET['vibes']
    user.save()

    context = {}
    context['user_to_display'] = user
    context['is_owner'] = user == request.user
    context['is_friend'] = user in request.user.friends.all()

    context['top_genre'] = get_top_genre(request, user)
    context['top_artist'] = get_top_artist(request, user)
    context['top_song'] = get_top_song(request, user)
    context['num_friends'] = get_num_friends(request, user)
    context['num_playlists'] = get_num_playlists(request, user)

    context['bg_color'] = 'blue-400'
    context['bubble_color'] = '[#7dd3fc]'

    return render(request, 'profile.html', context)


def playlist(request):
    context = {}
    if settings.DARKMODE == False:
        context['bg_color'] = '[#674846]'
        context['bubble_color'] = '[#fdbcb4]'
        context['darkmode'] = False
    else:
        context['bg_color'] = '[#002147]'
        context['bubble_color'] = '[#b0c4de]'
        context['darkmode'] = True

    sp = get_spotify_object(request)
    items = sp.current_user_recently_played(limit=20).get('items')
    tracks = []

    for item in items:
        uri = item.get('track').get('uri')
        track = get_or_create_track_from_uri(request, uri)
        tracks.append(track)

    random.shuffle(tracks)

    context['tracks'] = tracks
    return render(request, 'playlist.html', context)


def bar(request):
    return render(request, 'bar.html')


def playlistgenerate(request):
    context = {}
    context['user'] = request.user
    context['friends'] = request.user.friends.all()
    context["bg_color"] = "[#9f8170]"
    context["bubble_color"] = "[#ffebcd]"
    playlists = get_user_playlists(request)
    name = []
    for item in playlists:
        name.append(item.get('name'))

    dummy = []
    for i in range(len(name)):
        dummy.append(i)

    random.shuffle(name)
    pcounter = zip(name, dummy)

    context['playlists'] = pcounter
    return render(request, 'playlistgenerate.html', context)


def graph(request):
    return render(request, 'graph.html')


def tutorial(request):
    return render(request, 'tutorial.html')


def get_user_playlists(request):

    sp = get_spotify_object(request)
    iterations = 0
    playlists = []

    while (True):
        result = sp.current_user_playlists(limit=50, offset=iterations*50)
        items = result.get('items')
        if (len(items) == 0):
            break
        iterations += 1
        for playlist in items:
            if playlist.get('owner').get('id') == request.user.username:
                playlists.append(playlist)

    return playlists


def homepage(request):
    if 'darkMode' in request.GET:
        settings.DARKMODE = True

    if 'lightMode' in request.GET:
        settings.DARKMODE = False

    request_code = 0
    if 'add-friend' in request.GET:
        username = request.GET['add-friend']
        print("trying to add:", username)

        try:
            user = JMUser.objects.get(username=username)
            request.user.friends.add(user)
            print("friend added.")
            request_code = 1
        except ObjectDoesNotExist:
            print("doesn't exist!!")
            request_code = 2

    if 'remove-friend' in request.GET:
        username = request.GET['remove-friend']
        print("trying to remove:", username)
        try:
            user = JMUser.objects.get(username=username)
            request.user.friends.remove(user)
            print("friend removed.")
            request_code = 3
        except ObjectDoesNotExist:
            print("doesn't exist!!")
            request_code = 4

    friends = request.user.friends.all()
    if len(friends) >= 1:
        friend1 = friends[0].profile_picture
    else:
        friend1 = False

    if len(friends) >= 2:
        friend2 = friends[1].profile_picture
    else:
        friend2 = False

    if len(friends) >= 3:
        friend3 = friends[2].profile_picture
    else:
        friend3 = False

    context = {}

    context['user'] = request.user
    context['friends'] = request.user.friends.all()
    context['request_code'] = request_code

    context['friend1'] = friend1
    context['friend2'] = friend2
    context['friend3'] = friend3
    context["bg_color"] = "[#322c3d]"
    context["bubble_color"] = "[#8e3d81]"
    return render(request, 'homepage.html', context)


def profiledit(request):
    return render(request, 'profiledit.html')


def temp(request):

    context = {}
    context['user'] = request.user
    context['friends'] = request.user.friends.all()
    context["bg_color"] = "[#9f8170]"
    context["bubble_color"] = "[#ffebcd]"
    playlists = get_user_playlists(request)
    name = []
    for item in playlists:
        name.append(item.get('name'))

    context['playlists'] = name
    return render(request, 'temp.html', context)


def generate(request):
    sp = get_spotify_object(request)

    context = {}
    context['user'] = request.user
    context['friends'] = request.user.friends.all()
    context['artists'] = sp.current_user_top_artists().get('items')

    artists = sp.current_user_top_artists().get('items')
    artistNames = []
    for artist in artists:
        artistNames.append(artist.get('name'))

    context['artistNames'] = artistNames

    context['bg_color'] = '[#bc8f8f]'
    context['bubble_color'] = '[#3d0c02]'

    return render(request, 'generate.html', context)


def artist(request):
    sp: spotipy.Spotify = get_spotify_object(request)

    artist = '  '
    if 'aname' in request.POST:
        artist = request.POST['aname']
        if 'aname' in request.POST:
            # print(sp)
            result = sp.search(q=artist, limit=1, type='artist')
            for i, t in enumerate(result['artists']['items']):
                name = t['name']
                artistId = t['id']
                uri = t['uri']
                popularity = t['popularity']
                image_artist = t['images'][0]['url']

                holder = []
                print("yep")
                top_tracks = sp.artist_top_tracks(uri)
                print('nope')
                for track in top_tracks['tracks'][:5]:
                    # print('track    : ' + track['name'])
                    # print()
                    tempname = track['name']
                    if len(tempname) > 40:
                        tempname = tempname.split('-')[0]
                    holder.append(tempname)

                results = sp.artist_albums(uri, album_type='album')
                albums = results['items']

                album_titles = []

                for album in albums:
                    if len(album['name']) < 75:
                        album_titles.append(album['name'])

                seen = set()
                seen_add = seen.add
                album_titles = [x for x in album_titles if not (
                    x in seen or seen_add(x))]

                context = {
                    'render_intro': False,
                    'top_tracks': holder,
                    'album_titles': album_titles,
                    'image': image_artist,
                    'popularity': popularity,
                    'name': name,
                }
                # context = {
                #     'render_intro': False,
                #     'top_tracks': ['Jane\'s song', 'Cupids Arrow', 'Fake Song 3', 'No Ideas', 'John Robinson is the best'],
                #     'album_titles': ['Album Premier', 'Album deux: Springtime', 'Jayanthas Etude', 'Album Premier', 'Album deux: Springtime', 'Jayanthas Etude'],
                #     'image': image_artist,
                #     'popularity': popularity,
                #     'name': artist,
                # }
                return render(request, 'artist.html', context)
            return render(request, 'artist.html', {'error': True})
    context = {
        'render_intro': True,
        'dontrun': True,
    }

    context['bg_color'] = "[#595169]"
    context['bubble_color'] = "[#273ba9]"

    return render(request, 'artist.html', context)


def breakdown(request):

    sp: spotipy.Spotify = get_spotify_object(request)

    # ranges = ['short_term', 'medium_term', 'long_term']
    ranges = ['medium_term']
    top_song_ids = []
    all_artists = {}
    top_artists = []
    top_songs = []
    total_danceability = 0
    total_energy = 0
    total_instrumentalness = 0
    total_speechiness = 0
    num_songs = 0

    # if request.GET.get('quitting'):
    #     print('quitting')

    for sp_range in ranges:
        results = sp.current_user_top_tracks(time_range=sp_range, limit=50)
        for i, item in enumerate(results['items']):
            #print(i, item['name'], '//', item['artists'][0]['name'])
            top_song_ids.append(item['id'])
            top_songs.append(item['name'])

            artist_uri = item["artists"][0]['uri']
            # artist_info = sp.artist(artist_uri)

            # print(artist_info['genres'])

            if (item['artists'][0]['name'] in all_artists):
                all_artists[(item['artists'][0]['name'])] += 1
            else:
                all_artists[(item['artists'][0]['name'])] = 1

            artists_name_sorted = []
            artists_freq_sorted = []
            all_artists_sorted = sorted(
                all_artists, key=all_artists.get, reverse=True)
            for i in all_artists_sorted:
                artists_name_sorted.append(i)
                artists_freq_sorted.append(all_artists[i])

            # album = sp.album(item["album"]["external_urls"]["spotify"])
            # all_genres.append(album["genres"])

            metadata = sp.audio_features(item['uri'])[0]
            total_instrumentalness = total_instrumentalness + \
                metadata['instrumentalness']
            total_danceability = total_danceability + metadata['danceability']
            total_energy = total_energy + metadata['energy']
            total_speechiness = total_speechiness + metadata['speechiness']
            num_songs = num_songs + 1

        artists_fav = sp.current_user_top_artists(
            time_range=sp_range, limit=10)
        for i, item in enumerate(artists_fav['items']):
            top_artists.append(item['name'])

        total_instrumentalness = str(
            round((total_instrumentalness * 100)/num_songs, 2))
        total_danceability = str(
            round((total_danceability * 100)/num_songs, 2))
        total_energy = str(round((total_energy * 100)/num_songs, 2))
        total_speechiness = str(round((total_speechiness * 100)/num_songs, 2))

        context = {
            'top_songs': top_songs[:10],
            'top_artists': top_artists[:10],
            'sorted_artist_names': artists_name_sorted[:6],
            'sorted_artist_freq': artists_freq_sorted[:6],
            'instrumentalness': total_instrumentalness,
            'danceability': total_danceability,
            'energy': total_energy,
            'speechiness': total_speechiness
        }
        print()
        return render(request, 'breakdown.html', context)

    return render(request, 'breakdown.html', context={'error': True})


def gorb(request):
    sp: spotipy.Spotify = get_spotify_object(request)

    uris = []
    bad_repeat_uris = ["6OnfBiiSc9RGKiBKKtZXgQ",
                       "4HjwGX3pJKJTeOSDpT6GCo",
                       "2mY2q2kza9vvWKZz6JLTxS",
                       "4cOdK2wGLETKBW3PvgPWqT",
                       "0Jg602cHeMCnPez9baacIe",
                       "5ygDXis42ncn6kYG14lEVG"]

    bad_always_uris = ["12a51Wz9uxB0FahAPMHTde",
                       "0ik5szrSW9DvBF62OdYlqh",
                       "0AzD1FEuvkXP1verWfaZdv",
                       "2R8YJIea5IaRtVGka8uUyE",
                       "0CaHTGPAvGoDyycVvoMZgD",
                       "2Uu4AnnMTJpevC0IrwAuOW",
                       "2Wq2R59KXY8mW7sYGccrKA",
                       "66Crx53pJDyF3B2Nign13F",
                       "4WtguaQ8EOj7BfU06F2Lzz",
                       "0F09XNIuGq4kDtl5qeO7FR"]
    
    random_bad_uris = ["6epn3r7S14KUqlReYr77hA",
                       "1KEdF3FNF9bKRCxN3KUMbx",
                       "5RIVoVdkDLEygELLCniZFr",
                       "6nFYXpBgrNcZjbtNEuc6yR",
                       "315YiOWf8Yy7gOEOLpyWQs",
                       "66e2TRYYXe72Kj7iCBVkFC",
                       "29drzlJamuYPBRh1LPpXM4",
                       "1K2u31R6UAOtUPM4uSWQTc"]

    uri_string = ""
    uri_list = []
    GoodPlaylist = False
    if request.method == 'POST':
        GoodPlaylist = bool(random.getrandbits(1))
        if GoodPlaylist :
            print("GOODPLAYLIST SELECTED")
            results = sp.current_user_top_tracks(time_range=sp_range, 
                limit=14)
            for i, item in enumerate(results['items']):
                #print(i, item['name'], '//', item['artists'][0]['name'])
                uri_string += item['id']
                uri_string += ','
                top_songs.append(item['name'])

                artist_uri = item["artists"][0]['uri']
                top_tracks = sp.artist_top_tracks(artist_uri)

                for track in top_tracks['tracks'][:1]:
                    artist_uri = track['uri']
                    if artist_uri not in uri_list:
                        uri_list += artist_uri
                        uri_list += ','
            
            results2 = sp.current_user_top_artists(time_range=sp_range, limit=10)

            for i, item in enumerate(results2['items']):
                top_artist_tracks = sp.artist_top_tracks(item['uri'])
                for track in top_artist_tracks[:2]:
                    track_uri = track['uri']
                    if track_uri not in uri_list:
                        uri_list += track_uri
                        uri_list += ','
            uri_list = uri_list[:-1]

            print(uri_string)
        else :
            print("BADPLAYLIST SELECTED")

            #adds seven of one song
            randRepeat = random.randint(0, (len(bad_repeat_uris)-1))
            i=0
            while i < 7:
                uri_string += bad_repeat_uris[randRepeat]
                uri_string += ','
                i = i + 1
            
            #adds all of these songs
            for uri2 in bad_always_uris:
                uri_string += uri2
                uri_string += ','
            
            #adds half of these songs
            reduced_bad_uris = random.sample(random_bad_uris, 4)
            for uri3 in reduced_bad_uris:
                uri_string += uri3
                uri_string += ','
            
            uri_string = uri_string[:-1]

            print(uri_string)
    #convert uris to string comma separated


    context = {
        'pre_result': True,
    }

    return render(request, 'goodorbadplaylist.html', context)


def base(request):
    return render(request, 'base.html')


def login_user(request):

    login_django_user(request)

    update_user_stats(request)

    return redirect('welcome')
    # return render(request, "friends.html")


def friends(request):
    context = {}
    context['user'] = request.user
    context['friends'] = request.user.friends.all()
    context["bg_color"] = "[#322c3d]"
    context["bubble_color"] = "[#8e3d81]"

    request_code = 0
    if 'add-friend' in request.GET:
        username = request.GET['add-friend']
        print("trying to add:", username)

        try:
            user = JMUser.objects.get(username=username)
            request.user.friends.add(user)
            print("friend added.")
            request_code = 1
        except ObjectDoesNotExist:
            print("doesn't exist!!")
            request_code = 2

    if 'remove-friend' in request.GET:
        username = request.GET['remove-friend']
        print("trying to remove:", username)
        try:
            user = JMUser.objects.get(username=username)
            request.user.friends.remove(user)
            print("friend removed.")
            request_code = 3
        except ObjectDoesNotExist:
            print("doesn't exist!!")
            request_code = 4

    context['request_code'] = request_code

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
    api_test(request)
    return render(request, 'test.html')


def api_test(request):
    sp = get_spotify_object(request)

    print("Trying user API call:")
    pprint(sp.current_user())
    print("")

    print("Trying track API call: ")
    pprint(sp.track("11dFghVXANMlKmJXsNCbNl"))
    print("")

    print("Trying artist API call: ")
    pprint(sp.artist("0TnOYISbd1XYRBk9myaseg"))
    print("")

    pass

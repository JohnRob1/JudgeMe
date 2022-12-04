from distutils.log import debug
from pprint import pprint
from urllib.request import HTTPRedirectHandler
from django.shortcuts import render, HttpResponseRedirect, redirect, HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.urls import is_valid_path
from django.conf import settings
from django.http import JsonResponse
import random
from django.core.files import File
from django.core.files.images import ImageFile

from .forms import ImageForm, uploadedImage

#post imports---------
from .Spotify_post import Credentials

#end imports-------------

from .util_auth import generate_url, create_token_info, login_django_user, get_spotify_object
from .profile_stats import get_or_create_track_from_uri

from .models import *
from .profile_stats import update_user_stats, get_top_artist, get_top_genre, get_top_song, get_num_friends, get_num_playlists, get_music_taste, get_user_playlists

import spotipy
import os
import random


share_var = ""


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
    print(request.session['token'])
    #print("my code here----------")
    #Sujal(request)
    #print("my code here------------")

    return redirect('login')


def create_token(code):
    token_info = create_token_info(code=code)
    if token_info == None:
        return None

    return token_info['access_token']

#----------------------------

def success(request):

    context = {}
    context["bg_color"] = "[#355e3b]"
    context["bubble_color"] = "[#518634]"
    return render(request, 'success.html', context)

#-----------------------------
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
    #Sujal(request)
    context = {}
    context["bg_color"] = "[#322c3d]"
    context["bubble_color"] = "[#8e3d81]"
    return render(request, 'tutorial.html', context)


def judge(request):
    context = {}
    context['friends'] = request.user.friends.all()
    # context['playlists'] = request.user.playlists.all()
    context['me'] = request.user
    if request.user.music_taste == -1:
        get_music_taste(request, request.user)
    context['music_taste'] = request.user.music_taste
    if "friend" in request.GET:
        friend = JMUser.objects.get(display_name=request.GET.get("friend"))
        return result(request, friend)
    # if "playlist" in request.GET:
    #     playlist = Playlist.objects.get(name=request.GET.get("playlist"))
    #     context['playlists'] = {}
    #     for friend in context.get('friends'):
    #         context[friend] = []
    #         for playlist in friend.playlists:
    #             context[friend].append(playlist)
    #     return friend_playlist(request, context, playlist)
    return render(request, 'judge.html', context)

# def friend_playlist(request, context, playlist):
    
#     return render(request, 'friend_playlist.html', context)


def music_tastes(request):
    context = {}
    friends = {}
    context['friends'] = []
    for friend in request.user.friends.all():
        if friend.music_taste != -1:
            if friend.music_taste in friends:
                friends[friend.music_taste].append(friend)
            else:
                friends[friend.music_taste] = []
                friends[friend.music_taste].append(friend)
    for value in sorted(list(friends.keys())):
        for friend in friends[value]:
            context['friends'].append(friend)

    return render(request, 'music_tastes.html', context)

def result(request, friend):

    f_dict = {}
    u_dict = {}
    if friend.music_taste == -1:
        f_dict = get_music_taste(request, friend)

    if request.user.music_taste == -1:
        u_dict = get_music_taste(request, request.user)

    dark_mode = "Dark Mode"
    if settings.DARKMODE is False: dark_mode = "Light Mode"

    if abs(request.user.music_taste - friend.music_taste) < 25:
        if settings.DARKMODE is False:
            f = open('theme/static/light_mode_gifs/comps.txt', 'r')
        else:
            f = open('theme/static/dark_mode_gifs/comps.txt', 'r')
    else:
        if settings.DARKMODE is False:
            f = open('theme/static/light_mode_gifs/insults.txt', 'r')
        else:
            f = open('theme/static/dark_mode_gifs/insults.txt', 'r')
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
        'agreeablesness': u_dict.get('agreeableness'),
        'conscientiousness': u_dict.get('conscientiousness'),
        'openness': u_dict.get('openness'),
        'emotional_stability': u_dict.get('emotional_stability'),
        'extraverted': u_dict.get('extraverted'),
        'agreeableness_f': f_dict.get('agreeableness'),
        'concientiousness_f': f_dict.get('concientiousness'),
        'openness_f': f_dict.get('openness'),
        'emotional_stability_f': f_dict.get('emotional_stability'),
        'extraverted_f': f_dict.get('extraverted'),
        'dark_mode': dark_mode
    }
    return render(request, 'result.html', context)

def experiment(request):
    if request.method == "POST":
        form=ImageForm(data=request.POST,files=request.FILES)
        if form.is_valid():
            form.save()
            obj=form.instance
            return render(request,"experiment.html",{"obj":obj})
    else:
        form=ImageForm()
        img=Image.objects.all()
    return render(request,"experiment.html",{"img":img,"form":form})

def generateOptions(request):
    settings.SIZE = request.GET.get('size', None)
    pprint(settings.SIZE)
    artistString = request.GET.get('artist', None)
    settings.ARTIST = artistString[2:len(artistString) - 2].split("\",\"")
    pprint(settings.ARTIST)
    response = {}
    return JsonResponse(response)

def profile(request):
    sp = get_spotify_object(request)

    user = request.user
    if "user" in request.GET:
        try:
            user = JMUser.objects.get(username=request.GET.get('user'))
        except:
            user = None
            pass

    if "recalculate" in request.GET:
        update_user_stats(request)

    if "about" in request.GET:
        user.about = request.GET['about']
    if "vibes" in request.GET:
        user.vibes = request.GET['vibes']
    
    #user.save()
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

    if request.method == "POST":
        try:
            form=ImageForm(files=request.FILES)
            form.Meta.store_image = request.FILES
            user.uploaded_image = form.Meta.store_image['image']
            user.save()
        except:
            return HttpResponse("Oops you clicked upload instaed of save when editing bio. Try again but click save so that you're not posting image")
            #return HttpResponseRedirect("../profile/")

    context['custom_image'] = user.uploaded_image
    return render(request, 'profile.html', context)


def playlist(request):
    token = request.session['token']
    user_id = request.user.username
    context = {}
    if settings.DARKMODE == False:
        context['bg_color'] = '[#674846]'
        context['bubble_color'] = '[#fdbcb4]'
        context['darkmode'] = False
    else:
        context['bg_color'] = '[#002147]'
        context['bubble_color'] = '[#b0c4de]'
        context['darkmode'] = True

    tracks = []
    song_uri = ""
    track_name = []
    track_uri = {}
    sp = get_spotify_object(request)

    pprint(settings.SIZE)

    if settings.SIZE == 0 or settings.SIZE == '0':
        settings.SIZE = 20

    if settings.SIZE == 100 or settings.SIZE == '100':
        settings.SIZE = 50
        items = sp.current_user_top_tracks(settings.SIZE).get("items")
        for item in items:
            uri = item['uri']
            track = get_or_create_track_from_uri(request, uri)
            tracks.append(track)
    
    items = sp.current_user_top_tracks(settings.SIZE).get("items")
    for item in items:
        uri = item['uri']
        song_uri += uri + ","
        track = get_or_create_track_from_uri(request, uri)
        tracks.append(track)
        track_uri[track.name] = uri
        track_name.append(track.name)

    pname = ""
    if settings.DARKMODE == False:
        pname = "Sunny Days"
    else:
        pname = "Messy Midnights"
        
    
    song_uri = song_uri[:-1]
    wizard = Credentials(token, user_id)
    if request.method == "POST":
        if request.POST.get('sendplaylist') == 'test':
            playlist_id = wizard.create_playlist(pname)
            response = wizard.add_songs_to_playlist(song_uri)
            print(response)
            print("Post registered")
            return HttpResponseRedirect("../success/")
        elif request.POST.get('qsong') in track_name:
            my_uri = track_uri[request.POST.get('qsong')]
            wizard.add_song_to_queue(my_uri)
            print("Success")
            return HttpResponseRedirect("../playlist/")
    
    random.shuffle(tracks)

    """ 
    song_uri = ""
    for item in items:
        #pprint(item)
        uri = item.get('track').get('uri')
        song_uri += uri + ','
    """
    
    #song_uri = song_uri[:-1]
    #cred = Credentials(token, user_id)

    # context['songNames1'] = songNames[:20]
    # context['songNames2'] = songNames[20:]
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

def homepage(request):
    if 'darkMode' in request.GET:
        settings.DARKMODE = True

    if 'lightMode' in request.GET:
        settings.DARKMODE = False

    settings.SIZE = 0

    settings.ARTIST = []

    request_code = 0
    if 'add-friend' in request.GET:
        display_name = request.GET['add-friend']
        print("trying to add:", display_name)

        try:
            user = JMUser.objects.get(display_name=display_name)
            request.user.friends.add(user)
            print("friend added.")
            request_code = 1
        except ObjectDoesNotExist:
            print("doesn't exist!!")
            request_code = 2

    if 'remove-friend' in request.GET:
        display_name = request.GET['remove-friend']
        print("trying to remove:", display_name)
        try:
            user = JMUser.objects.get(display_name=display_name)
            request.user.friends.remove(user)
            print("friend removed.")
            request_code = 3
        except ObjectDoesNotExist:
            print("doesn't exist!!")
            request_code = 4

    friends = request.user.friends.all()
    besties = []
    if len(friends) >= 1:
        besties.append(friends[0])
        friend1 = friends[0]
    else:
        friend1 = False

    if len(friends) >= 2:
        besties.append(friends[1])
        friend2 = friends[1]
    else:
        friend2 = False

    if len(friends) >= 3:
        besties.append(friends[2])
        friend3 = friends[2]
    else:
        friend3 = False

    #image_lst = Image.objects.all()


    context = {}

    context['user'] = request.user
    context['friends'] = request.user.friends.all()
    context['request_code'] = request_code
    context['custom_image'] = request.user.uploaded_image

    context['besties'] = besties
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
    pre_result = True
    bad_repeat_uris = ["spotify:track:6OnfBiiSc9RGKiBKKtZXgQ",
                       "spotify:track:4HjwGX3pJKJTeOSDpT6GCo",
                       "spotify:track:2mY2q2kza9vvWKZz6JLTxS",
                       "spotify:track:4cOdK2wGLETKBW3PvgPWqT",
                       "spotify:track:0Jg602cHeMCnPez9baacIe",
                       "spotify:track:5ygDXis42ncn6kYG14lEVG"]

    bad_always_uris = ["spotify:track:12a51Wz9uxB0FahAPMHTde",
                       "spotify:track:0ik5szrSW9DvBF62OdYlqh",
                       "spotify:track:0AzD1FEuvkXP1verWfaZdv",
                       "spotify:track:2R8YJIea5IaRtVGka8uUyE",
                       "spotify:track:0CaHTGPAvGoDyycVvoMZgD",
                       "spotify:track:2Uu4AnnMTJpevC0IrwAuOW",
                       "spotify:track:2Wq2R59KXY8mW7sYGccrKA",
                       "spotify:track:66Crx53pJDyF3B2Nign13F",
                       "spotify:track:4WtguaQ8EOj7BfU06F2Lzz",
                       "spotify:track:0F09XNIuGq4kDtl5qeO7FR"]
    
    random_bad_uris = ["spotify:track:6epn3r7S14KUqlReYr77hA",
                       "spotify:track:1KEdF3FNF9bKRCxN3KUMbx",
                       "spotify:track:5RIVoVdkDLEygELLCniZFr",
                       "spotify:track:6nFYXpBgrNcZjbtNEuc6yR",
                       "spotify:track:315YiOWf8Yy7gOEOLpyWQs",
                       "spotify:track:66e2TRYYXe72Kj7iCBVkFC",
                       "spotify:track:29drzlJamuYPBRh1LPpXM4",
                       "spotify:track:1K2u31R6UAOtUPM4uSWQTc"]

    uri_string = ""
    tracks = []
    GoodPlaylist = False
     
    if request.method == 'POST':
        pre_result = False
        GoodPlaylist = bool(random.getrandbits(1))
        #GoodPlaylist = False
        if request.POST.get('sendplaylist') == 'test':
            print("AJSKLDJASKLJDLKASJDLKASJDLKADS")
            playlist_title = ""
            if GoodPlaylist: 
                playlist_title = "JudgeMe GoodTime Jams"
            else :
                playlist_title = "JUDGEMENT HATH FALLEN"
            token = request.session['token']
            user_id = request.user.username
            wizard = Credentials(token, user_id)
            playlist_id = wizard.create_playlist(playlist_title)
            response = wizard.add_songs_to_playlist(settings.URI_LIST)
            print(response) 
            return HttpResponseRedirect("../homepage/")
        if GoodPlaylist :
            print("GOODPLAYLIST SELECTED")
            results = sp.current_user_top_tracks(time_range='medium_term', 
                limit=14)
            for i, item in enumerate(results['items']):
                #print(i, item['name'], '//', item['artists'][0]['name'])
                uri_string += item['uri']
                uri_string += ','
                tracks.append(get_or_create_track_from_uri(request, item['uri']))

                artist_uri = item["artists"][0]['uri']
                top_tracks = sp.artist_top_tracks(artist_uri)

                for track in top_tracks['tracks'][:1]:
                    artist_uri = track['uri']
                    if artist_uri not in uri_string:
                        uri_string += artist_uri
                        uri_string += ','
                        tracks.append(get_or_create_track_from_uri(request, artist_uri))

            
            results2 = sp.current_user_top_artists(time_range='medium_term', limit=2)

            for i, item in enumerate(results2['items']):
                top_artist_tracks = sp.artist_top_tracks(item['uri'])
                for track in top_artist_tracks['tracks'][:2]:
                    track_uri = track['uri']
                    if track_uri not in uri_string:
                        uri_string += track_uri
                        uri_string += ','
                        tracks.append(get_or_create_track_from_uri(request, track_uri))

            uri_string = uri_string[:-1]
            settings.URI_LIST = uri_string
            print(uri_string)
        else :
            print("BADPLAYLIST SELECTED")

            #adds seven of one song
            randRepeat = random.randint(0, (len(bad_repeat_uris)-1))
            i=0
            while i < 7:
                uri_string += bad_repeat_uris[randRepeat]
                uri_string += ','
                tracks.append(get_or_create_track_from_uri(request, bad_repeat_uris[randRepeat]))
                i = i + 1
            
            #adds all of these songs
            for uri2 in bad_always_uris:
                uri_string += uri2
                uri_string += ','
                tracks.append(get_or_create_track_from_uri(request, uri2))
            
            #adds half of these songs
            reduced_bad_uris = random.sample(random_bad_uris, 4)
            for uri3 in reduced_bad_uris:
                uri_string += uri3
                uri_string += ','
                tracks.append(get_or_create_track_from_uri(request, uri3))
            
            uri_string = uri_string[:-1]
            settings.URI_LIST = uri_string

            print(uri_string)

        # playlist_title = ""
        # if GoodPlaylist: 
        #     playlist_title = "JudgeMe GoodTime Jams"
        # else :
        #     playlist_title = "JUDGEMENT HATH FALLEN"
        # token = request.session['token']
        # user_id = request.user.username
        # wizard = Credentials(token, user_id)
        # playlist_id = wizard.create_playlist(playlist_title)
        # response = wizard.add_songs_to_playlist(uri_string)
        # print(response)
    #convert uris to string comma separated


    context = {
        'pre_result': pre_result,
        'Goodplaylist' : GoodPlaylist,
        'uris' : uri_string,
        'tracks' : tracks,
    }
    print(tracks)

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




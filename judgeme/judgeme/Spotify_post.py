import json
import requests

class Credentials:
    
    def __init__(self, spotfify_token, spotify_user_id, playlist_id="", playlist_uri=""):
        self.spotify_token = spotfify_token
        self.spotify_user_id = spotify_user_id
        self.playlist_id = playlist_id
        self.playlist_uri = playlist_uri

    def create_playlist(self, playlist_name):
        query = "https://api.spotify.com/v1/users/{}/playlists".format(self.spotify_user_id)

        request_body = json.dumps({
            "name": "{}".format(playlist_name),
            "description": "You added this from JudgeMe, Nice job!",
            "public": True,

        })

        header = {"Content-Type":"application/json", 
        "Authorization": "Bearer {}".format(self.spotify_token),
        }

        response = requests.post(query, data=request_body, headers=header)
        response_json = response.json()

        self.playlist_id = response_json["id"]
        return response_json["id"]
    
    def add_songs_to_playlist(self, playlist_uris):

        query = "https://api.spotify.com/v1/playlists/{}/tracks?uris={}".format(
        self.playlist_id, 
        playlist_uris)

        #for item in self.playlist_uri:
        #    print(item)

        header = {"Content-Type":"application/json", 
        "Authorization": "Bearer {}".format(self.spotify_token),
        }

        response = requests.post(query, headers=header)
        response_json = response.json()
        return response_json

    def add_a_song(self, song_uri):


        query = "https://api.spotify.com/v1/playlists/{}/tracks?uris={}".format(
        self.playlist_id, 
        song_uri)

        header = {"Content-Type":"application/json", 
        "Authorization": "Bearer {}".format(self.spotify_token),
        }

        response = requests.post(query, headers=header)
        response_json = response.json()

        return response_json
    
    def add_song_to_queue(self, song_uri):

        query = "https://api.spotify.com/v1/me/player/queue?uri={}".format(song_uri)

        header = {"Content-Type":"application/json", 
        "Authorization": "Bearer {}".format(self.spotify_token),
        }
        requests.post(query, headers=header)

        return "SuccessFully Posted"

class Scope:

    def __init__(self, scope=""):
        self.scope = scope
    
    def createScope(self):    
        scopes = [ 
            "user-top-read", 
            "user-library-read",
            "playlist-read-private",
            "playlist-modify-public",
            "user-read-private",
            "user-read-email",
            "user-read-recently-played",
            "user-modify-playback-state",
        ]

        for item in scopes:
            self.scope += item + ' '
        return self.scope

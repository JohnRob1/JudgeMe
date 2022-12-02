# from unittest.util import _MAX_LENGTH
from django.db import models
from django.contrib.auth.models import AbstractUser, User

class JMUser(AbstractUser):
    profile_picture = models.CharField(max_length=256)
    display_name = models.CharField(max_length=256)

    top_track_name = models.CharField(max_length=256)
    top_tracks = models.ManyToManyField("Track", blank=True)
    top_artists = models.ManyToManyField("Artist", blank=True)

    playlist_count = models.SmallIntegerField(default=-1)
    playlists = models.ManyToManyField("Playlist", blank=True)

    friends = models.ManyToManyField("JMUser", blank=True)

    about = models.CharField(max_length=256)
    vibes = models.CharField(max_length=256)

    agreeableness = models.FloatField(default=0)
    conscientiousness = models.FloatField(default=0)
    emotional_stability = models.FloatField(default=0)
    extravertedness = models.FloatField(default=0)
    openness = models.FloatField(default=0)
    music_taste = models.IntegerField(default=-1)

    def __str__(self):
        return self.display_name

    
class Playlist(models.Model):
    name = models.CharField(max_length=256)
    uri = models.CharField(max_length=512)
    playlist_pic = models.CharField(max_length=256)
    tracks = models.ManyToManyField("Track", blank=True)
    playlist_music_taste = models.FloatField(default=-1)


class Artist(models.Model):
    name = models.CharField(max_length=256)
    uri = models.CharField(max_length=512)
    top_genre = models.CharField(max_length=256)
    picture = models.CharField(max_length=256)
    # location = models.CharField(max_length=256)

    def __str__(self):
        return self.name

    def __str__(self):
        return f"{self.name}"

class Track(models.Model):
    name = models.CharField(max_length=256)
    artist_name = models.CharField(max_length=256)
    uri = models.CharField(max_length=256)
    audio_preview = models.CharField(max_length=256)
    picture = models.CharField(max_length=256)
    # artist = models.ForeignKey(
    #     Artist, on_delete=models.CASCADE, related_name='tracks')
    # album = models.ForeignKey(
    #     Album, on_delete=models.CASCADE, related_name='tracks')
    # collaborators = models.ManyToManyField(
    #     Artist, related_name='collaborations')

    # index = models.PositiveIntegerField()
    # name = models.CharField(max_length=256)
    # audio = models.FileField()

    def __str__(self):
        return self.name


class Album(models.Model):
    id = models.CharField(max_length=32, primary_key=True, unique=True)

    artist = models.ForeignKey(
        Artist, on_delete=models.CASCADE)

    name = models.CharField(max_length=256)
    image = models.URLField(null=True)
    tracks = models.ManyToManyField(Track)
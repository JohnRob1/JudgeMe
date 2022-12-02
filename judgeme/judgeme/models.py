# from unittest.util import _MAX_LENGTH
from django.db import models
from django.contrib.auth.models import AbstractUser, User


class JMUser(AbstractUser):
    profile_picture = models.CharField(max_length=256)

    top_tracks = models.ManyToManyField("Track", blank=True)
    playlist_count = models.SmallIntegerField(default=-1)

    friends = models.ManyToManyField("JMUser", blank=True)

    about = models.CharField(max_length=256)
    vibes = models.CharField(max_length=256)

    music_taste = models.FloatField(default = -1)

    def __str__(self):
        return self.username


class Artist(models.Model):
    name = models.CharField(max_length=256)
    location = models.CharField(max_length=256)

    def __str__(self):
        return f"{self.name}"

class Track(models.Model):
    name = models.CharField(max_length=256)
    uri = models.CharField(max_length=32)
    picture = models.URLField(null=True)
    artist = models.ForeignKey(
        Artist, on_delete=models.CASCADE)


    danceability = models.DecimalField(max_digits=4, decimal_places=3)
    speechiness = models.DecimalField(max_digits=4, decimal_places=3)
    acousticness = models.DecimalField(max_digits=4, decimal_places=3)
    valence = models.DecimalField(max_digits=4, decimal_places=3)
    instrumentalness = models.DecimalField(max_digits=4, decimal_places=3)
    energy = models.DecimalField(max_digits=4, decimal_places=3)
    liveness = models.DecimalField(max_digits=4, decimal_places=3)

    @property
    def get_fields_names(self):
        return [f.name for f in Features._meta.fields if f.name != 'id']

    @property
    def get_features(self):
        dict_of_features = {
            f: getattr(self, f) for f in self.get_fields_names
        }
        return dict_of_features
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
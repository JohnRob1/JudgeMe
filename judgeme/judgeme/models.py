# from unittest.util import _MAX_LENGTH
from django.db import models
from django.contrib.auth.models import AbstractUser, User


class JMUser(AbstractUser):
    profile_picture = models.CharField(max_length=256)

    top_tracks = models.ManyToManyField("Track", blank=True)

    friends = models.ManyToManyField("JMUser", blank=True)

    def __str__(self):
        return self.username


class Artist(models.Model):
    name = models.CharField(max_length=256)
    location = models.CharField(max_length=256)


class Album(models.Model):
    artist = models.ForeignKey(
        Artist, on_delete=models.CASCADE, related_name='albums')

    name = models.CharField(max_length=256)
    release_date = models.DateField()
    # cover = models.ImageField()


class Track(models.Model):
    name = models.CharField(max_length=256)
    uri = models.CharField(max_length=512)
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

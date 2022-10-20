from django.db import models


class User(models.Model):
    username = models.CharField(max_length=256)
    password = models.CharField(max_length=256)

class Artist(models.Model):
    name = models.CharField(max_length=256)
    location = models.CharField(max_length=256)

class Album(models.Model):
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='albums')

    name = models.CharField(max_length=256)
    release_date = models.DateField()
    # cover = models.ImageField()

class Track(models.Model):
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='tracks')
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='tracks')
    collaborators = models.ManyToManyField(Artist, related_name='collaborations')

    index = models.PositiveIntegerField()
    name = models.CharField(max_length=256)
    audio = models.FileField()
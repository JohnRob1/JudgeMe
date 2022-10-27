from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    # username = models.CharField(max_length=256)
    # password = models.CharField(max_length=256)
    profile_picture = models.CharField(max_length=256)

    friends = models.ManyToManyField("User", blank=True)


# class FriendList(models.Model):
#     user = models.OneToOneField(
#         User, on_delete=models.CASCADE, related_name='user')

#     def __str__(self):
#         return self.user.username

#     def add_friend(self, account):
#         if not account in self.friends.all():
#             self.friends.add(account)
#             self.save()

#     def remove_friend(self, account):
#         if account in self.friends.all():
#             self.friends.remove(account)
#             self.save()


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
    artist = models.ForeignKey(
        Artist, on_delete=models.CASCADE, related_name='tracks')
    album = models.ForeignKey(
        Album, on_delete=models.CASCADE, related_name='tracks')
    collaborators = models.ManyToManyField(
        Artist, related_name='collaborations')

    index = models.PositiveIntegerField()
    name = models.CharField(max_length=256)
    audio = models.FileField()

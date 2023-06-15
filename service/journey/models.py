from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class UserProfile(models.Model):
    user_id = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.TextField(blank=True)
    last_name = models.TextField(blank=True)
    bio = models.TextField(blank=True)
    profile_img = models.ImageField(upload_to='profile_images', default='blank-profile-picture.png')
    avatar = models.CharField(max_length=200)
    about = models.CharField(max_length=500)


class Trip(models.Model):
    start_point = models.CharField(max_length=200)
    finish_point = models.CharField(max_length=200)
    departure_date = models.DateTimeField()
    transport_type = models.CharField(max_length=200)
    available_seats = models.IntegerField()
    status = models.CharField(max_length=200)

    users = models.ManyToManyField(User, related_name='trips_users', blank=True)


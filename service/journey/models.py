from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class UserProfile(models.Model):
    # id
    user_id = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.CharField(max_length=200)
    about = models.CharField(max_length=500)


class Trip(models.Model):
    trip_name = models.CharField(max_length=200)
    start_point = models.CharField(max_length=200)
    end_point = models.CharField(max_length=200)
    departure_date = models.DateTimeFieldField()
    transport_type = models.CharField(max_length=200)
    available_seats = models.IntegerField()

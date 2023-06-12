from django.shortcuts import render
from rest_framework import viewsets
from .models import Trip, UserProfile
from .serializers import TripSerializer, UserProfileSerializer


# Create your views here.


class TripViewSet(viewsets.ModelViewSet):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer


class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = TripSerializer

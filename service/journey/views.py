from django.shortcuts import render
from .models import Trip, UserProfile
from .serializers import TripSerializer, UserProfileSerializer

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, pagination, status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response


# Create your views here.


class TripViewSet(viewsets.ModelViewSet):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['trip_name']
    filterset_fields = ['trip_name', 'start_point', 'end_point', 'departure_date', 'transport_type']
    ordering_fields = ['departure_date']
    pagination_class = pagination.PageNumberPagination

    @action(detail=False, methods=['get'])
    def my_trips(self, request):
        user = request.user
        trips = Trip.objects.filter(users=user)
        serializer = TripSerializer(trips, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    @action(detail=False, methods=['post'])
    def join_trip(self, request):
        trip_id = request.data.get('trip_id')
        user = request.user

        try:
            trip = Trip.objects.get(pk=trip_id)
        except Trip.DoesNotExist:
            return Response({'message': 'Поездка не существует.'}, status=status.HTTP_404_NOT_FOUND)

        if trip.users.filter(pk=user.pk).exists():
            return Response({'message': 'Вы уже присоединены к этой поездке.'}, status=status.HTTP_400_BAD_REQUEST)

        if trip.available_seats <= 0:
            return Response({'message': 'Нет доступных мест в этой поездке.'}, status=status.HTTP_400_BAD_REQUEST)

        trip.users.add(user)
        trip.available_seats -= 1
        return Response({'message': 'Вы успешно присоединились к поездке.'}, status=status.HTTP_200_OK)


class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer




from .models import Trip, UserProfile, Reviews
from .serializers import TripSerializer, UserProfileSerializer, UserSerializer, ReviewsSerializer

from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import User
from rest_framework import  status, generics
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination


class TripView(ListAPIView):
    authentication_classes = [TokenAuthentication]

    queryset = Trip.objects.all()
    serializer_class = TripSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['start_point', 'finish_point']
    filterset_fields = ['start_point', 'finish_point', 'departure_date', 'transport_type']
    ordering_fields = ['departure_date']
    pagination_class = PageNumberPagination

    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TripDetailView(APIView):
    authentication_classes = [TokenAuthentication]

    def post(self, request):
        serializer = TripSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(creator=request.user, status='new')
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        trip_id = request.data.get('trip_id')
        trip = self.get_trip(trip_id)
        if not trip:
            return Response({'message': 'Trip not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = TripSerializer(trip, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        trip_id = request.data.get('trip_id')
        trip = self.get_trip(trip_id)
        if not trip:
            return Response({'message': 'Trip not found.'}, status=status.HTTP_404_NOT_FOUND)

        trip.delete()
        return Response({'message': 'Trip is successfully deleted'}, status=status.HTTP_200_OK)

    def get(self, request):
        trip_id = request.GET.get('trip_id')
        trip = self.get_trip(trip_id)
        if not trip:
            return Response({'message': 'Trip not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = TripSerializer(trip)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_trip(self, trip_id):
        try:
            return Trip.objects.get(pk=trip_id)
        except Trip.DoesNotExist:
            return None


class TripUserView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Trip.objects.all()
    serializer_class = TripSerializer

    def get(self, request):
        user = request.user
        trips = Trip.objects.filter(users=user)
        if trips:
            serializer = TripSerializer(trips, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'message': "You don't have any trips"}, status=status.HTTP_200_OK)

    def post(self, request):
        trip_id = request.data.get('trip_id')
        user = request.user

        try:
            trip = Trip.objects.get(pk=trip_id)
        except Trip.DoesNotExist:
            return Response({'message': 'Trip does nit exist.'}, status=status.HTTP_404_NOT_FOUND)

        if trip.users.filter(pk=user.pk).exists():
            return Response({'message': 'You have already joined to trip.'}, status=status.HTTP_400_BAD_REQUEST)

        if trip.available_seats <= 0:
            return Response({'message': 'Sorry, there are no available seats.'}, status=status.HTTP_400_BAD_REQUEST)

        trip.users.add(user)
        trip.status = "progress"
        trip.available_seats -= 1
        trip.save()
        return Response({'message': 'Success! You joined to trip.'}, status=status.HTTP_200_OK)

    def delete(self, request):
        trip_id = request.data.get('trip_id')
        try:
            trip = Trip.objects.get(pk=trip_id)
        except Trip.DoesNotExist:
            return Response({'message': 'Trip does nit exist.'}, status=status.HTTP_404_NOT_FOUND)

        trip.users.remove(request.user)
        trip.available_seats += 1
        trip.save()
        return Response({'message': 'Success! You deleted from trip.'}, status=status.HTTP_200_OK)


class UserProfileView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_user_profile(self, user_id):
        try:
            return UserProfile.objects.get(user_id=user_id)
        except UserProfile.DoesNotExist:
            return None

    def get(self, request):
        user_id = request.GET.get('user_id')
        user_profile = self.get_user_profile(user_id)
        if user_profile:
            serializer = UserProfileSerializer(user_profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response("User profile does not exist.", status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        user_id = request.user.id
        user_profile = self.get_user_profile(user_id)
        if user_profile:
            return Response("User profile already exists.", status=status.HTTP_400_BAD_REQUEST)

        data_profile = request.data
        data_profile['user_id'] = user_id
        serializer = UserProfileSerializer(data=data_profile)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        user_id = request.user.id
        user_profile = self.get_user_profile(user_id)
        data_profile = request.data
        data_profile['user_id'] = user_id
        if user_profile:
            serializer = UserProfileSerializer(user_profile, data=data_profile)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("User profile does not exist.", status=status.HTTP_404_NOT_FOUND)


class UserCreateAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not User.objects.filter(username=username).exists():
            return Response({'message': 'Username does not exist'},
                            status=status.HTTP_404_NOT_FOUND)
        user = User.objects.get(username=username)

        if not user.check_password(password):
            return Response({'message': 'Incorrect password'},
                            status=status.HTTP_401_UNAUTHORIZED)
        token, _ = Token.objects.get_or_create(user=user)

        return Response({'token': token.key}, status=status.HTTP_200_OK)


class ReviewView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = request.GET.get('user_id')
        reviews = Reviews.objects.filter(r_user=user_id)
        if reviews:
            serializer = ReviewsSerializer(reviews, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'message': "User don't have review"}, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ReviewsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

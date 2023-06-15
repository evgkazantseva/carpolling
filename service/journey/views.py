from .models import Trip, UserProfile
from .serializers import TripSerializer, UserProfileSerializer, UserSerializer

from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import User
from rest_framework import viewsets, pagination, status, generics
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated


# Create your views here.
class TripViewSet(viewsets.ModelViewSet):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['trip_name']
    filter_fields = ['trip_name', 'start_point', 'end_point', 'departure_date', 'transport_type']
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
            return Response({'message': 'Trip does nit exist.'}, status=status.HTTP_404_NOT_FOUND)

        if trip.users.filter(pk=user.pk).exists():
            return Response({'message': 'You have already joined to trip.'}, status=status.HTTP_400_BAD_REQUEST)

        if trip.available_seats <= 0:
            return Response({'message': 'Sorry, there are no available seats.'}, status=status.HTTP_400_BAD_REQUEST)

        trip.users.add(user)
        trip.available_seats -= 1
        return Response({'message': 'Success! You joined to trip.'}, status=status.HTTP_200_OK)


class UserProfileViewSet(APIView):
    authentication_classes = [TokenAuthentication]

    def get_user_profile(self, user_id):
        try:
            return UserProfile.objects.get(user_id=user_id)
        except UserProfile.DoesNotExist:
            return None

    def create_user_profile(self, user_id, data):
        data['user_id'] = user_id
        serializer = UserProfileSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return serializer.data
        else:
            raise serializer.ValidationError(serializer.errors)

    def get(self, request):
        user_id = request.user.id
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

        serializer = UserProfileSerializer(data=request.data)
        if serializer.is_valid():
            profile_data = self.create_user_profile(user_id, request.data)
            return Response(profile_data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        user_id = request.user.id
        user_profile = self.get_user_profile(user_id)
        if user_profile:
            serializer = UserProfileSerializer(user_profile, data=request.data)
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
        token = Token.objects.get(username)

        return Response({'token': 'token.key'}, status=status.HTTP_200_OK)

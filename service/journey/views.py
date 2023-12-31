from .models import Trip, UserProfile
from .serializers import TripSerializer, UserProfileSerializer, UserSerializer

from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import User
from rest_framework import viewsets, pagination, status, generics
from rest_framework.decorators import action
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

    def post(self, request):
        serializer = TripSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(creator=request.user, status='new')
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        trip = self.get_trip(pk)
        if not trip:
            return Response({'message': 'Trip not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = TripSerializer(trip, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        trip = self.get_trip(pk)
        if not trip:
            return Response({'message': 'Trip not found.'}, status=status.HTTP_404_NOT_FOUND)

        trip.delete()
        return Response({'message': 'Trip is successfully deleted'}, status=status.HTTP_200_OK)

    def get_trip(self, pk):
        try:
            return Trip.objects.get(pk=pk)
        except Trip.DoesNotExist:
            return None

# Create your views here.
# class TripViewSet(viewsets.ModelViewSet):
#     authentication_classes = [TokenAuthentication]
#     queryset = Trip.objects.all()
#     serializer_class = TripSerializer
#
#     filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
#     search_fields = ['trip_name']
#     filter_fields = ['trip_name', 'start_point', 'end_point', 'departure_date', 'transport_type']
#     ordering_fields = ['departure_date']
#     pagination_class = pagination.PageNumberPagination
#
#     def perform_create(self, serializer):
#         serializer.save(creator=self.request.user)
#
#     def update(self, request, *args, **kwargs):
#         partial = kwargs.pop('partial', False)
#         instance = self.get_object()
#         serializer = self.get_serializer(instance, data=request.data, partial=partial)
#         serializer.is_valid(raise_exception=True)
#         serializer.save(creator=request.user)
#         return Response(serializer.data)
#
#     @action(detail=False, methods=['get'])
#     def my_trips(self, request):
#         user = request.user
#         trips = Trip.objects.filter(users=user)
#         serializer = TripSerializer(trips, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)
#
#     @action(detail=False, methods=['post'])
#     def join_trip(self, request):
#         trip_id = request.data.get('trip_id')
#         user = request.user
#
#         try:
#             trip = Trip.objects.get(pk=trip_id)
#         except Trip.DoesNotExist:
#             return Response({'message': 'Trip does nit exist.'}, status=status.HTTP_404_NOT_FOUND)
#
#         if trip.users.filter(pk=user.pk).exists():
#             return Response({'message': 'You have already joined to trip.'}, status=status.HTTP_400_BAD_REQUEST)
#
#         if trip.available_seats <= 0:
#             return Response({'message': 'Sorry, there are no available seats.'}, status=status.HTTP_400_BAD_REQUEST)
#
#         trip.users.add(user)
#         trip.available_seats -= 1
#         return Response({'message': 'Success! You joined to trip.'}, status=status.HTTP_200_OK)


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

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserProfileView, TripView, UserCreateAPIView, LoginView

router = DefaultRouter()
# router.register('trips', TripViewSet, basename='trip')


urlpatterns = [
    path('', include(router.urls)),
    # path('trips/join_trip/', TripViewSet.as_view({'post': 'join_trip'}), name='join_trip'),
    path('register/', UserCreateAPIView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('user/profile/', UserProfileView.as_view(), name='user-profile'),
    path('trips/', TripView.as_view(), name='trip-list'),
    path('trips/<int:pk>/', TripView.as_view(), name='trip-detail'),
]

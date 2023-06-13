from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserProfileViewSet, TripViewSet, UserCreateAPIView, LoginView

router = DefaultRouter()
router.register(r'trips', TripViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('trips/join_trip/', TripViewSet.as_view({'post': 'join_trip'}), name='join_trip'),
    path('register/', UserCreateAPIView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('user/profile', UserProfileViewSet.as_view({'get': 'list'}), name='userprofile')
]

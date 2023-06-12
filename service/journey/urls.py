from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserProfileViewSet, TripViewSet

router = DefaultRouter()
router.register(r'trips', TripViewSet)
router.register(r'user', UserProfileViewSet)
urlpatterns = [
    path('', include(router.urls)),
    path('trips/join_trip/', TripViewSet.as_view({'post': 'join_trip'}), name='join_trip'),
]

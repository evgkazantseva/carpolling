from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserProfileViewSet, TripViewSet

router = DefaultRouter()
router.register(r'trips', TripViewSet)
router.register(r'user', UserProfileViewSet)
urlpatterns = [
    path('', include(router.urls)),
]

from rest_framework.routers import DefaultRouter
from .views import UserRegistrationViewSet, UserLoginViewset
from django.urls import path, include

router = DefaultRouter()
router.register(r'register', UserRegistrationViewSet, basename='user-registration')
router.register(r'login', UserLoginViewset, basename='user-login')
# router.register(r'profile', UserProfileViewset, basename='user-profile')  

urlpatterns = [
    path('', include(router.urls)),
]

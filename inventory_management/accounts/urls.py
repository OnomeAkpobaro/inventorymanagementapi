from rest_framework.routers import DefaultRouter
from .views import UserViewSet, UserProfileViewset
from django.urls import path

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')  
router.register(r'userprofile', UserProfileViewset, basename='userprofile')  

urlpatterns = router.urls

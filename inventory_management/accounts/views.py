from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from django.contrib.auth import get_user_model
from .serializers import UserRegistrationSerializer,UserLoginSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
# Create your views here.

# Get the active User model as defined in settings.py
User = get_user_model()

class UserRegistrationViewSet(ReadOnlyModelViewSet):
    """
    ViewSet for handling user registration.
    Inherits from ReadOlyModelViewSet to provide read-only operations by default.
    """

    # Query all users from the database
    queryset = User.objects.all()

    # Specify the serializer class for user registration
    serializer_class = UserRegistrationSerializer

    # Alllow any user (authenticated or not) to access this ViewSet
    permission_classes = [AllowAny]

    def create(self, request):
        """
        Custom method to handle user registration.

        Args:
            request: HTTP request object containing user registration data
        
        Returns:
            Response: JSON response with registration status and user details or error messages if validation fails 
        """

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "status": "success",
                "message": "User Registration successful",
                "user_id": user.id
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class UserLoginViewset(viewsets.ModelViewSet):
    """
    ViewSet for handling user login operations.
    Inherits from ModelViewSet to provide full CRUD operations.

    """

    # Query all users from the database
    queryset = User.objects.all()

    # Specify the serializer class for user login
    serializer_class = UserLoginSerializer

    # Allow any user to access this viewset
    permission_classes =[AllowAny]

    @action(detail=False, methods=['post'])
    def login(self, request):
        """
        Custom action to handle user login.
        with @action decorator to create a custom endpoint at /login/

        Args:
            request: HTTP request object containing login credentials

        Returns:
            Response: JSON response wit authentication token if login is successful or error messages if validation fails
        """
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            return Response({
                "status": "success",
                "token": serializer.validated_data['token']
            }, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



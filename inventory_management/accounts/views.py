from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from django.contrib.auth import get_user_model
from .serializers import UserRegistrationSerializer,UserLoginSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
# Create your views here.

User = get_user_model()

class UserRegistrationViewSet(ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request):
        """
        Creates custom method to handle user registration
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
    queryset = User.objects.all()
    serializer_class = UserLoginSerializer
    permission_classes =[AllowAny]

    @action(detail=False, methods=['post'])
    def login(self, request):
        """
        Handles user login and return authentication token
        """
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            return Response({
                "status": "success",
                "token": serializer.validated_data['token']
            }, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class UserProfileViewset(viewsets.ModelViewSet):
#     """
#     Viewset for user profile operations
#     provides endpoint for ciewing and updating user profiles
#     """

#     serializer_class = UserProfileSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         """
#         Filter queryset to return only the current user's profile
#         """
#         return User.objects.filter(id=self.request.user.id)
#     def update(self, request, *args, **kwargs):
#         """
#         Custom update method to handle profile updates
#         """
#         partial = kwargs.pop('partial', False)
#         instance = self.get_object()
#         serializer = self.get_serializer(instance, data=request.data, partial=partial)

#         if serializer.is_valid():
#             self.perform_update(serializer)
#             return Response({
#                 "status": "success",
#                 "message": "Profile Update Successful",
#                 "data": serializer.data
#             })
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
#     @action(detail=False, methods=['get'])
#     def current_user(self, request):
#         """
#         Endpoint to get current uswer's profile
#         """
#         serializer = self.get_serializer(request.user)
#         return Response(serializer.data)
        
        


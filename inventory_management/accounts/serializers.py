from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
# from .models import UserProfile



User = get_user_model()
class UserRegistrationSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True, validators=[UniqueValidator(queryset=get_user_model().objects.all())])
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    
    class Meta:
        model = User
        fields = ("id", "username", "email", "password", "password2", "first_name", 'last_name')

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return data
    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password']
        )
        user.save()
        return user
    
class UserLoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)
    class Meta:
        model = User
        fields = ("id", "username", "password",)

    def create(self, validated_data):
        """
        Removes 'user' from validated_data if it exists
        """
        validated_data.pop('user', None)
        return User.objects.create(**validated_data)

    def validate(self, data):
        """
        Validate user credentials
        """
        try:
            user = User.objects.get(username=data['username'])
            if not user.check_password(data['password']):
                raise serializers.ValidationError("Invalid Credentials")
            data['user'] = user
            return data
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found.")



# class UserProfileSerializer(serializers.ModelSerializer):
    

#     class Meta:
#         model = User
#         fields = ['id', 'user', 'email', 'phone_number', 'created_at', 'updated_at']
#         read_only_fields = ['id', 'created_at', 'updated_at']

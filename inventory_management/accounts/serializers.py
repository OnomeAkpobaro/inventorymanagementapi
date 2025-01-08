from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

#Get the active User model
User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration that handles creating new user accounts.

    Features:
    - Validates unique email addresses
    - Ensures password meets Django's validation requirements
    - Confirms password match through password2 field
    - Handles creation of new user instances
    """
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True, validators=[UniqueValidator(queryset=get_user_model().objects.all())])    #Ensures email is unique
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])                        #Password won't be included in response, and uses Django's password validation
    password2 = serializers.CharField(write_only=True, required=True)
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    
    class Meta:
        model = User
        fields = ("id", "username", "email", "password", "password2", "first_name", 'last_name')

    def validate(self, data):
        """
        Validate that password and password2 match.

        Args:
            data: (dict): Dictionary containing the serializer data

        Returns:
            dict: Validated data if passwords match

        Raises:
            ValidationError: If password don't mmatch
        """

        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return data
    
    
    def create(self, validated_data):
        """
        Create and return a new user instance.

        Args:
            Validated_data (dict): Validated data from serializer
        Returns:
            User: Newly created user instance
        """


        #Remove password2 as it's not needed for user creation
        validated_data.pop('password2')


        #Create new user instance using create_user method
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password']
        )
        user.save()
        return user
    

class UserLoginSerializer(serializers.ModelSerializer):
    """
    Serializer for handling user login authentication

    Features:
    - Validates user credentials
    - Checks if user exists
    - Verifies password
    """

    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ("id", "username", "password",)

    def create(self, validated_data):
        """
       Create method 
        """
        validated_data.pop('user', None)
        return User.objects.create(**validated_data)

    def validate(self, data):
        """
        Validate user credentials by checking username existence and password correctness.

        Args:
            data (dict): Dictionary containing username and password
        
        Returns:
            dict: Validated data with user object if credentials are valid
        
        Raises: 
            ValidationError: If user doesn't exist or credentials are invalid
        """
        try:
            user = User.objects.get(username=data['username'])
            if not user.check_password(data['password']):
                raise serializers.ValidationError("Invalid Credentials")
            data['user'] = user
            return data
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found.")




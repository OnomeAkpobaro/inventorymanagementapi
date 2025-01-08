from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.conf import settings

class UserManager(BaseUserManager):

    """
    Custom user manager that extends Django's BaseUserManager
    Handles user creation and superuser creation with a custom validation logic.
    """
    def create_user(self, username, email, password):
        """
        Creates and saves a regular user with the given username, email, and password.

        Args:
            username (str): Unique username for the user
            email (str): Unique email address for the user
            password (str): User's password

        Raises:
            ValueError: If email or username is not provided
        
        Returns:
            User: created user instance
        """
        if not email:
            raise ValueError("Enter a valid email")
        if not username:
            raise ValueError("Enter a valid username")
        
        # Create new user instance with normalized email
        user = self.model(username=username, email=self.normalize_email(email)) #Normalizes email to lowercase domain
        user.set_password(password) #Handles password hashing
        user.save(using=self._db) #saves user to database
        return user
    
    def create_superuser(self, username, email, password):
        """
        Creates and saves a superuser with the given username, email, and password.

        Args:
            username (str): Unique username for the superuser
            email (str): Unique email address for the superuser
            password (str): Superuser's password

        Returns:
            User: Created superuser instance with admin priveleges
        """

        # Create regular user first
        user = self.create_user(username, email, password=password)
        
        #Add admin priviledges
        user.is_admin = True
        user.is_staff = True
        user.save(using=self._db)
        return user
    
class User(AbstractUser):
    """
    custom user model that extends Django's AbstractUser.
    Provides custom implementation of the default Django User model

    Attributes:
        username (str): Unique identifier for the user
        email (str): Unique email address for the user
        USERNAME_FIELD (str): Field used for authentication (username in this case)
        REQUIRED_FIELDS (list): Additional required fields during user creation
        objects (UserManager): Custom manager for user operations
  
    """
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True, max_length=255)

    
    USERNAME_FIELD = 'username'     #Specifies which field to use for authentication
    REQUIRED_FIELDS = ['email']     #Additional required fields during user creation
    objects = UserManager()         #Assigns custom user manager

    def __str__(self):
        """
        String representation of the user object.

        Returns:
            str: username of the user
        """
        return self.username
    

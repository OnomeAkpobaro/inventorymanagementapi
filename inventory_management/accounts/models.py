from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.conf import settings

class UserManager(BaseUserManager):
    def create_user(self, email, password):
        """
        Create new user
        """
        if not email:
            raise ValueError("Enter a valid email")
        user = self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password):
        """
        Create a superuser
        """
        user = self.create_user(email, password=password)
        user.is_admin = True
        user.is_staff = True
        user.save(using=self._db)
        return user
    
class User(AbstractUser):
    """
  
    """
    email = models.EmailField(unique=True, max_length=255)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()

    def __str__(self):
        return self.username
    
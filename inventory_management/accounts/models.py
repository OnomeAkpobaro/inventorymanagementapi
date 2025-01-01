from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.conf import settings

class UserManager(BaseUserManager):
    def create_user(self, username, email, password):
        """
        Create new user
        """
        if not email:
            raise ValueError("Enter a valid email")
        if not username:
            raise ValueError("Enter a valid username")
        user = self.model(username=username, email=self.normalize_email(email))
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, email, password):
        """
        Create a superuser
        """
        user = self.create_user(username, email, password=password)
        user.is_admin = True
        user.is_staff = True
        user.save(using=self._db)
        return user
    
class User(AbstractUser):
    """
    custom user
  
    """
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True, max_length=255)

    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    objects = UserManager()

    def __str__(self):
        return self.username
    
# class UserProfile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     phone_number = models.CharField(max_length=15, blank=True)
#     address = models.TextField(blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return self.user.username
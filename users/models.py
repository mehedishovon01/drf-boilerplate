from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

class User(AbstractUser):
    """
    Custom User model that extends Django's AbstractUser.
    This model adds additional fields to store more detailed information about the user,
    such as their profile picture, nickname, address details, etc.
    :attributes: field name & structure
    """
    nick_name = models.CharField(max_length=255)
    address = models.TextField(blank=True, null=True, default='')
    state = models.CharField(max_length=100, blank=True, null=True, default='')
    city = models.CharField(max_length=100, blank=True, null=True, default='')
    street = models.CharField(max_length=150, blank=True, null=True, default='')
    house = models.CharField(max_length=150, blank=True, null=True, default='')

    def __str__(self):
        """
        String representation of the User model.
        Returns the user's email if available, otherwise their username.
        :return: str
        """
        return self.email or str(self.username)


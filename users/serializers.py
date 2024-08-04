from django.contrib.auth.models import Group
from rest_framework import serializers
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions as django_exceptions
from rest_framework import exceptions as drf_exceptions
from django.db import IntegrityError, transaction
from config import exceptions as custom_exception
from config import settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.utils.translation import gettext_lazy as _


# Set the default User Model here
User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        read_only_fields = ['username', 'email']


class SignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            User._meta.pk.name,
            'username',
            'email',
            'password',
        )

    def validate(self, attrs):
        user = User(**attrs)
        password = attrs.get('password')
        try:
            validate_password(password, user)
        except django_exceptions.ValidationError as e:
            messages = [_(message) for message in e.messages]
            raise serializers.ValidationError({'password': messages})
        return attrs

    def create(self, validated_data):
        try:
            user = self.perform_create(validated_data)
        except IntegrityError:
            raise custom_exception.AlreadyExists(
                _('The provided email address already has an account.'))
        return user

    @staticmethod
    def perform_create(validated_data):
        with transaction.atomic():
            user = User.objects.create_user(**validated_data)
            # if settings.SEND_ACTIVATION_EMAIL:
            #     user.is_active = False
            #     user.save(update_fields=['is_active'])
        return user
    

class LoginSerializer(TokenObtainPairSerializer):
    def validate(cls, user):
        data = super().validate(user)
        
        data['token'] = {
            'refresh': data.pop('refresh'),
            'access': data.pop('access')
        }
        
        user = User.objects.get(username=cls.user.username)
        user_serilizer = UserSerializer(user)

        data['user_data'] = user_serilizer.data

        return data
    

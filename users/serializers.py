from rest_framework import serializers
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions as django_exceptions
from django.db import IntegrityError, transaction
from config import exceptions as custom_exception
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError
from django.contrib.auth.models import update_last_login
from rest_framework.exceptions import AuthenticationFailed
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse


# Set the default User Model here
User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model, providing methods to serialize and deserialize user instances. This serializer includes all fields 
    from the User model. Sets certain fields as read-only to ensure they cannot be modified through the serializer.
    Configures the 'password' field to be write-only for security reasons.
    Attributes: Meta (class): Contains configuration options for the serializer.
    """
    class Meta:
        model = User
        fields = [
            'id', 'first_name', 'last_name', 'email', 'nick_name',
            'address', 'state', 'city', 'street', 'house', 'is_staff', 'is_active', 'last_login',
        ]
        # Fields that should not be modified via the serializer
        read_only_fields = ['email']
        # Ensure the password is not readable in serialized output
        extra_kwargs = {
            'password': { 'write_only': True }
        }

    def update(self, instance, validated_data):
        """
        Override the update method to handle custom update logic if needed. 
        :args: instance (User): validated_data (dict):
        :returns: user instance.
        """
        return super().update(instance, validated_data)


class SignUpSerializer(serializers.ModelSerializer):
    """
    This serializer is being called when any user want to register/sign-up. It will set the input type to password for security in forms.
    And ensure the password is not included in serialized output.
    """
    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            User._meta.pk.name,
            'email',
            'password',
        )

    password = serializers.CharField(
        style={'input_type': 'password'}, 
        write_only=True
        )

    def validate(self, attrs):
        """
        Custom validation logic for the password field. Create a User instance with the provided attributes.
        Get the password from the attributes.
        Finally, Validate the password using Django's built-in validators, If fails, capture the error messages
        :param: self, attributes
        :return: validated attributes
        """
        user = User(**attrs)
        password = attrs.get('password')
        try:
            validate_password(password, user)
        except django_exceptions.ValidationError as e:
            messages = [_(message) for message in e.messages]
            raise serializers.ValidationError({'password': messages})
        return attrs

    def create(self, validated_data):
        """
        Custom create method to handle user creation. Perform the actual creation of the user
        :param: self, attributes
        :return: newly created instance
        """
        try:
            validated_data['email'] = validated_data['email']
            validated_data['username'] = validated_data['email']
            validated_data['password'] = validated_data['password']
            user = self.perform_create(validated_data)
        except IntegrityError as e:
            raise custom_exception.AlreadyExists(
                _(f'Error: {e}'))
        return user

    @staticmethod
    def perform_create(validated_data):
        """
        Use a database transaction to ensure atomicity of the user creation.
        Create a new user with the validated data.
        :param: attributes
        :return: instance
        """
        with transaction.atomic():
            user = User.objects.create_user(**validated_data)
            user.is_active = False
            user.save(update_fields=['is_active'])
        return user
    

class LoginSerializer(TokenObtainPairSerializer):
    """
    Serializer for handling user login. It extends the TokenObtainPairSerializer to customize the validation process and modify the output.
    The primary functions of this serializer are ensure that the password field is handled securely and is not included in the serialized output.
    To structure the response to include both tokens and user data.
    """
    def validate(self, validate_data):
        """
        Validate the login credentials and generate tokens. Also includes additional user data in the response.
        :returns: dict with `tokens` and `serialized user_data`
        """
        active_user = get_object_or_404(User, username=validate_data['email'])
        if not active_user.check_password(validate_data['password']):
            raise AuthenticationFailed("No User matches the given query.")
        if not active_user.is_active:
            raise AuthenticationFailed("Please verify your account first.")
        
        data = super().validate(validate_data)
        data['token'] = {
            'refresh': data.pop('refresh'),
            'access': data.pop('access')
        }
        user = User.objects.get(username=self.user.email)
        user_serilizer = UserSerializer(user)
        data['user_data'] = user_serilizer.data
        update_last_login(None, self.user)

        return data
    

class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for handling password change requests.
    Validates the old password and ensures the new password meets
    the required validation criteria.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_old_password(self, value):
        """
        Validate the old password provided by the user.
        Ensures that the old password matches the user's current password.
        :param value: old password
        :returns: validated old password if correct.
        :raises ValidationError: If the old password does not match the user's current password.
        """
        user = self.context['request'].user
        if not user.check_password(value):
            raise ValidationError("Old password is incorrect.")
        return value

    def validate_new_password(self, value):
        """
        Validate the new password according to Django's password policies.
        :param value: new password
        :returns: validated new password if it meets the validation criteria
        :raises ValidationError: If the new password does not meet the validation criteria.
        """
        validate_password(value)
        return value

    def update(self, instance, validated_data):
        """
        Update the user's password with the new password provided.
        :param instance: instance whose password is being updated.
        :param validated_data: The validated data containing the new password.
        :returns: The updated user instance with the new password.
        """
        instance.set_password(validated_data['new_password'])
        instance.save()
        return instance
        

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        """
        Validate that the provided email corresponds to a user account.
        If no user is found with the provided email, raise a validation error.
        """
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("No user is associated with this email address.")
        return value

    def save(self, request):
        """
        Generate a password reset token and send it to the user's email.
        This method creates a URL for password reset and sends it via email.
        """
        email = self.validated_data['email']
        user = User.objects.get(email=email)
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        # Generate the reset URL
        reset_url = request.build_absolute_uri(
            reverse('reset-password-confirm', kwargs={'uidb64': uid, 'token': token})
        )

        # Send email
        context = {
            'reset_url': reset_url,
            'user': user,
        }
        subject = "Password Reset Requested"
        message = render_to_string('reset_password_email.html', context)
        send_mail(subject, message, None, [user.email])


class ResetPasswordConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    uidb64 = serializers.CharField()
    token = serializers.CharField()

    def validate(self, attrs):
        """
        Validate the provided token and user ID.
        Decode the user ID and verify the token. If invalid, raise a validation error.
        """
        try:
            uid = urlsafe_base64_decode(attrs['uidb64']).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError("Invalid reset link")

        if not default_token_generator.check_token(user, attrs['token']):
            raise serializers.ValidationError("Invalid reset link")

        attrs['user'] = user
        return attrs

    def save(self):
        """
        Save the new password for the user.
        This method sets the user's password to the new password provided.
        """
        user = self.validated_data['user']
        user.set_password(self.validated_data['new_password'])
        user.save()
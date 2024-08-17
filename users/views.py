from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import authenticate, get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.db import transaction
from users.serializers import (
    SignUpSerializer, 
    LoginSerializer, 
    LoginSerializer, 
    UserSerializer, 
    ChangePasswordSerializer,
    ResetPasswordSerializer,
    ResetPasswordConfirmSerializer
    )

# Set the default User Model here
User = get_user_model()

# Create views here.
class SignUpView(generics.CreateAPIView):
    """
    This class view for handling user registration. This view allows anyone to register a new user. 
    It handles POST requests by validating the incoming data and saving a new user instance.
    :attributes: permission_classes
    :return: serialized user data with a 201 status
    """
    permission_classes = [permissions.AllowAny]

    @csrf_exempt
    def post(self, serializer, *args, **kwargs):
        """
        This function handle the `POST` requests to register a new user.
        This method extracts the data from the request & validates the data using the SignUpSerializer. 
        Saves the new user instance if the data is valid. Returns a success response with the serialized user data.
        :args: request
        :returns: serialized user data and a status code of 201.
        """
        post_data = serializer.data
        user_serializer = SignUpSerializer(data=post_data)
        user_serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            user = user_serializer.save()
            self.send_verification_email(serializer, user)

        context = {
            'message': 'A mail has been sent to your mail address. Please verify before login.',
            'user_data': user_serializer.data,
        }
        return Response(context, status=status.HTTP_201_CREATED)
    
    def send_verification_email(self, request, user):
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        url = request.build_absolute_uri(reverse('verify-email', args=[uid, token]))

        subject = 'Verify your email'
        message = render_to_string('email_verification.html', {'url': url})
        send_mail(subject, message, 'mehedishovon01@gmail.com', [user.email])


class VerifyEmailView(generics.GenericAPIView):
    """
    This class view for handling email verification. This view allows newly register user to verify their account. 
    It handles get requests by validating the incoming data and save.
    :return: 200 OK or 400 BAD REQ
    """
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, uidb64, token):
        """
        Handles GET requests for email verification. This view is used to verify a user's email address 
        by decoding the provided user ID (`uidb64`) and validating the token sent to the user's email. 
        If the token is valid, the user's email is marked as verified in the database.
        :args:
            - request (HttpRequest): The request object containing metadata about the request.
            - uidb64 (str): The base64 encoded user ID.
            - token (str): The token used to verify the user's email.
        :returns:
            - response: successfully verified or if an error occurred (e.g., invalid token or user ID).
        """
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return Response({'message': 'Email verified successfully!'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid token or user ID'}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(TokenObtainPairView):
    """
    This class view for handling user login. This view uses the `TokenObtainPairView` from Django REST framework's Simple JWT 
    package to handle the generation of JWT tokens upon successful login.
    :attributes: serializer_class
    """
    serializer_class = LoginSerializer


class ProfileView(generics.RetrieveAPIView):  
    """
    This class view for retrieving the authenticated user's profile.
    This view allows an authenticated user to retrieve their own profile information.
    It uses the `RetrieveAPIView` from Django REST framework to handle GET requests.
    :attributes: serializer, permission, queryset
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        This function handle the `GET` requests to retrieve the authenticated user's profile.
        This method retrieves the user instance associated with the authenticated user. Serializes the user instance data.
        And returns the serialized data in the response with a status code of 200.
        :args: request
        :returns: serialized data and a status code.
        """
        # Retrieve the current authenticated user
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class UpdateProfileView(generics.UpdateAPIView):
    """
    View to update the authenticated user's profile data.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """
        Override get_object to return the authenticated user's instance.
        :returns: user's instance.
        """
        return self.request.user

    def put(self, request, *args, **kwargs):
        """
        Handle PUT requests to update the user's profile data.
        :args: request (Request):
        :returns: updated user data and a status code.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        """
        Handle PATCH requests to partially update the user's profile data.
        :args: request (Request):
        :returns: updated user data and a status code.
        """
        kwargs['partial'] = True
        return self.put(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        """
        Handle DELETE requests to partially delete the user's profile.
        :args: request (Request):
        :returns: status code.
        """
        instance = self.get_object()
        instance.delete()
        return Response({
            "message": "Your Account Has Been Deleted Successfully!"
            }, status=status.HTTP_200_OK)


class ChangePasswordView(generics.UpdateAPIView):
    """
    View for handling password changes for authenticated users.
    This view allows a user to change their password by providing
    the current password and a new password.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def get_object(self):
        """
        Override get_object to return the authenticated user's instance.
        :returns: user's instance.
        """
        return self.request.user

    def post(self, request, *args, **kwargs):
        """
        Handle POSTR requests to change the user's password.
        :args: request (Request):
        :returns: updated user data and a status code.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(instance=request.user)
            return Response({"message": "Password changed successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ResetPasswordView(generics.GenericAPIView):
    """
    View to handle password reset requests.
    This view validates the email and triggers the password reset process.
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = ResetPasswordSerializer

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests to initiate the password reset process.
        This method sends a password reset email to the user.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(request=request)
        return Response({"detail": "Password reset email has been sent."}, status=status.HTTP_200_OK)

class ResetPasswordConfirmView(generics.GenericAPIView):
    """
    View to handle password reset confirmations.
    This view allows the user to set a new password after clicking the reset link.
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = ResetPasswordConfirmSerializer

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests to set a new password.
        This method validates the reset token and saves the new password.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Password has been reset successfully."}, status=status.HTTP_200_OK)
    
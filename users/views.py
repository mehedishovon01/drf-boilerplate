from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from users.serializers import SignUpSerializer, LoginSerializer, LoginSerializer, UserSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import authenticate, get_user_model
from django.views.decorators.csrf import csrf_exempt


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
    def post(self, serializer):
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
        user_serializer.save()
        return Response(user_serializer.data, status=status.HTTP_201_CREATED)


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
    # queryset=User.objects.all()

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
    
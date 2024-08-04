from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from users.serializers import SignUpSerializer, LoginSerializer, LoginSerializer, UserSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import authenticate, get_user_model


# Set the default User Model here
User = get_user_model()

# Create views here.
class SignUpView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]

    def post(self, serializer):
        post_data = serializer.data
        user_serializer = SignUpSerializer(data=post_data)
        user_serializer.is_valid(raise_exception=True)
        user_serializer.save()
        return Response(user_serializer.data, status=status.HTTP_201_CREATED)


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer


class ProfileView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        user = User.objects.get(username=1)
        user_data = UserSerializer(user)
        return Response(user_data.data, status=status.HTTP_200_OK)
        
    
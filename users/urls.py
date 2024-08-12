from django.urls import path
from .views import (
    SignUpView, 
    LoginView, 
    ProfileView,
    UpdateProfileView
    )

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='user_signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/update/', UpdateProfileView.as_view()),
]

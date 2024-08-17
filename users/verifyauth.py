# # authentication.py
# from django.contrib.auth.backends import ModelBackend
# from django.contrib.auth import get_user_model
# from django.core.exceptions import PermissionDenied
# from rest_framework import generics, permissions, status
# from rest_framework.response import Response

# class EmailBackend(ModelBackend):
#     def authenticate(self, request, email=None, password=None, **kwargs):
#         UserModel = get_user_model()
#         try:
#             user = UserModel.objects.get(username=email)
#             print(user)
#             if not user.check_password(password):
#                 return None
#             if not user.is_active:
#                 return user.is_active
#                 # return Response('Please verify your account first')
#                 raise PermissionDenied("Please verify your account first.")
#             return user
#         except UserModel.DoesNotExist:
#             return None

from django.contrib import admin
from .models import *


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email')
    list_filter = ('username', 'first_name', 'last_name', 'email', 'state','city','street')

# Register the UserProfile model with the custom admin class
admin.site.register(User, UserAdmin)
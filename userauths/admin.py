from django.contrib import admin
from django.contrib.sessions.models import Session

from .models import User


# Register your models here.

class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'total_visits', 'is_staff', 'is_superuser')


admin.site.register(User, UserAdmin)

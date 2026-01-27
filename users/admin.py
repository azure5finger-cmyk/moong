from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class MyUserAdmin(UserAdmin):
    fieldsets = [
        ( None, {"fields" : ("username", "password","email", "phone")}),
        ( "활동 정보", {"fields" : ("nick_name", "location", "profile_image")}),
        ( "권한", { "fields": ("is_active", "is_staff", "is_superuser")}),
        ( "중요한 일정", { "fields": ("last_login", "date_joined")}),
    ]
    
    list_display = ("username", "nick_name")


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


class UserAdmin(BaseUserAdmin):
    """커스텀 User 모델을 위한 Admin"""
    
    # 리스트 화면에서 보여줄 필드
    list_display = ['username', 'nick_name', 'email', 'ddomoong', 'date_joined']
    
    # 검색 가능한 필드
    search_fields = ['username', 'nick_name', 'email']
    
    # 필터
    list_filter = ['is_staff', 'is_superuser', 'date_joined']
    
    # 상세 화면 필드 그룹핑
    fieldsets = BaseUserAdmin.fieldsets + (
        ('추가 정보', {
            'fields': ('nick_name', 'profile_image', 'location', 'ddomoong', 'phone', 'gender')
        }),
    )
    
    # 새 사용자 추가 화면
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('추가 정보', {
            'fields': ('nick_name', 'email', 'location', 'phone', 'gender')
        }),
    )


# User 모델 등록
admin.site.register(User, UserAdmin)
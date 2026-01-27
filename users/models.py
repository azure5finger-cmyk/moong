from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    
    # 기본 프로필 정보
    nick_name = models.CharField(
        max_length=50, 
        unique=True, 
        verbose_name='닉네임'
    )
    profile_image = models.ImageField(
        upload_to='profile_images/%Y/%m/%d/',
        blank=True, 
        null=True,  
        verbose_name='프로필 이미지'
    )
    bio = models.TextField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name='자기소개'
    )
    
    # 개인 정보
    phone = models.CharField(
        max_length=20, 
        null=True, 
        blank=True, 
        verbose_name='전화번호'
    )
    gender = models.CharField(
        max_length=1,
        choices=[('M', '남성'), ('F', '여성'), ('O', '기타')],
        null=True,
        blank=True,
        verbose_name='성별'
    )
    gender_visible = models.BooleanField(
        default=True,
        verbose_name='성별 공개'
    )
    
    # 위치 정보
    location = models.ForeignKey(
        'locations.Location',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',  
        verbose_name='주 활동 지역'
    )
    
    # 활동 정보
    ddomoong = models.IntegerField(
        default=0, 
        verbose_name='또뭉(좋아요 수)'
    )
    
    # Django admin 페이지를 한글로 보기 위해
    class Meta:
        verbose_name = '사용자'
        verbose_name_plural = '사용자'
        db_table = 'users'
    
    # 닉네임 우선
    def __str__(self):
        return self.nick_name or self.username
    
    def increase_ddomoong(self):
        """또뭉 증가"""
        self.ddomoong += 1
        self.save(update_fields=['ddomoong']) 
    
    def decrease_ddomoong(self):
        """또뭉 감소"""
        if self.ddomoong > 0:
            self.ddomoong -= 1
            self.save(update_fields=['ddomoong']) 
    





    


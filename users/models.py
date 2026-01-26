# users/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """커스텀 User 모델"""
    
    # AbstractUser 기본 제공 필드들:
    # username, password, email, first_name, last_name
    # is_staff, is_active, is_superuser, date_joined, last_login, email
    
    # 추가 커스텀 필드들
    nick_name = models.CharField(max_length=50, verbose_name='닉네임')
    profile_image = models.ImageField(
        upload_to='profile_images/%Y/%m/%d/',
        verbose_name='프로필 이미지'
    )
    
    location = models.ForeignKey('locations.Location',
                                on_delete=models.SET_NULL,
                                null=True,
                                blank=True,
                                related_name='user_location',
                                help_text="기본 활동 지역",
                                db_column='location_id',
                                verbose_name='주소'
                                )
    
    ddomoong = models.IntegerField(default=0, verbose_name='또뭉(좋아요 수)')
    phone = models.CharField(max_length=20, null=True, blank=True, verbose_name='전화번호')
    gender = models.CharField(
        max_length=1,
        choices=[('M', '남성'), ('F', '여성'), ('O', '기타')],
        null=True,
        blank=True,
        verbose_name='성별'
    )
    
    class Meta:
        verbose_name = '사용자'
        verbose_name_plural = '사용자'
        db_table = 'users'  # 테이블명을 'users'로 지정
    
    def __str__(self):
        return self.username if self.username else self.nick_name
    
    # def increase_ddomoong(self):
    #     """또뭉 증가"""
    #     self.ddomoong += 1
    #     self.save()
    
    # def decrease_ddomoong(self):
    #     """또뭉 감소"""
    #     if self.ddomoong > 0:
    #         self.ddomoong -= 1
    #         self.save()

    # hashtags/models.py (또는 posts/models.py 안에)


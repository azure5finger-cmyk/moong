from django.db import models
from django.contrib.auth.models import AbstractUser
from locations.models import Location
from django.core.validators import RegexValidator

phone_regex = RegexValidator(
    regex = r"^010-\d{4}-\d{4}$",
    message="전화번호는 010-XXXX-XXXX 형식이어야 합니다."
    )

class User(AbstractUser):
    phone = models.CharField(validators=[phone_regex],
                             max_length=13,
                             blank=True,
                             unique=True,
                             help_text="휴대전화 번호")
    
    email = models.EmailField(unique = True,
                              blank=False,
                              help_text="이메일 주소")
    
    nick_name = models.CharField(max_length=100)

    location = models.ForeignKey(to=Location,
                                 on_delete=models.SET_NULL,
                                 null=True,
                                 blank=True,
                                 related_name='user_location',
                                 help_text="기본 활동 지역"
                                 )
    
    profile_image = models.ImageField(
        upload_to = "users/profile_images/",
        blank = True,
        null = True,
        help_text = "프로필 이미지"
    )
    
    def __str__(self):
        return self.username
    
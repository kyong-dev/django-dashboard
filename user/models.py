from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, username, email=None, password=None, **extra_fields):
        if not username:
            raise ValueError("The Username field must be set")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        user = self.create_user(
            username=username,
            password=password,
            email=email,
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, null=True, blank=True, verbose_name="이메일")
    username = models.CharField(max_length=50, unique=True, verbose_name="유저네임")
    password = models.CharField(max_length=128, verbose_name="비밀번호")
    is_active = models.BooleanField(default=True, verbose_name="활성화 여부")
    is_staff = models.BooleanField(default=False, verbose_name="스태프 여부")
    registered_at = models.DateTimeField(auto_now_add=True, verbose_name="가입일")

    objects = UserManager()

    USERNAME_FIELD = "username"

    class Meta:
        db_table = "user"
        verbose_name = "사용자"
        verbose_name_plural = "사용자"

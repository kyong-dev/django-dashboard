from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _


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
    email = models.EmailField(unique=True, null=True, blank=True, verbose_name=_("이메일"))
    username = models.CharField(max_length=50, unique=True, verbose_name=_("유저네임"))
    password = models.CharField(max_length=128, verbose_name=_("비밀번호"))
    is_active = models.BooleanField(default=True, verbose_name=_("활성화 여부"))
    is_staff = models.BooleanField(default=False, verbose_name=_("스태프 여부"))
    registered_at = models.DateTimeField(auto_now_add=True, verbose_name=_("가입일시"))
    deactivated_at = models.DateTimeField(blank=True, null=True, verbose_name=_("비활성화일시"))

    objects = UserManager()

    USERNAME_FIELD = "username"

    class Meta:
        db_table = "user"
        verbose_name = _("사용자")
        verbose_name_plural = _("사용자")

from typing import Any

from django import forms
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

from unfold.widgets import UnfoldAdminTextInputWidget

from .models import User


class UserForm(forms.ModelForm):
    username = forms.CharField(
        validators=[
            RegexValidator(
                regex=r"^[\w.@+-]+$",
                message=_("50자 이하 문자, 숫자 그리고 @/./+/-/_만 가능합니다."),
            ),
        ],
        widget=UnfoldAdminTextInputWidget(attrs={"placeholder": _("50자 이하 문자, 숫자 그리고 @/./+/-/_만 가능합니다.")}),
        help_text=_("50자 이하 문자, 숫자 그리고 @/./+/-/_만 가능합니다."),
        label=_("유저네임"),
    )

    class Meta:
        model = User
        fields = "__all__"
        help_texts = {
            "is_active": _("이 사용자가 활성화되어 있는지를 나타냅니다. 계정을 삭제하는 대신 이것을 선택 해제하세요."),
        }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        if not hasattr(self, "initial") or self.initial is None:
            self.initial = {}

    def save(self, commit: bool = True) -> User:
        user = super().save(commit=False)
        password = self.cleaned_data.get("password")
        if password and (user.id is None or not password.startswith("pbkdf2_sha256$")):
            user.set_password(password)

        user.save()

        return user

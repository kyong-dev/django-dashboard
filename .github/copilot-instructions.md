# Django 모델 작성 가이드라인

## 1. 기본 구조

### 1.1 Import 순서

```python
# 표준 라이브러리
from decimal import Decimal

# Django 관련
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

# 프로젝트 내 앱 모듈
from your_app.models.other_model import OtherModel

User = get_user_model()
```

### 1.2 클래스 정의 기본 형태

```python
class ModelName(models.Model):
    # 1. 상수 정의 (CHOICES)
    STATUS_CHOICES = [
        ("active", _("Active")),
        ("inactive", _("Inactive")),
    ]

    # 2. 필드 정의
    # 3. 메서드 정의
    # 4. Meta 클래스
```

## 2. 필드 정의 규칙

### 2.1 필드 순서

1. Primary Key (보통 자동생성되므로 생략)
2. Foreign Key 필드
3. 일반 데이터 필드
4. 선택사항 필드 (blank=True, null=True)
5. 타임스탬프 필드 (created_at, updated_at)

### 2.2 필드 작성 패턴

```python
# 기본 패턴
field_name = models.FieldType(
    max_length=100,           # 필수 옵션
    unique=True,              # 제약 조건
    blank=True, null=True,    # 선택 사항
    default="default_value",  # 기본값
    choices=CHOICES,          # 선택지
    verbose_name=_("필드명")   # 관리자 페이지 표시명
)

# Foreign Key 패턴
related_model = models.ForeignKey(
    RelatedModel,
    on_delete=models.CASCADE,
    related_name="reverse_relation_name",
    verbose_name=_("관련 모델")
)
```

### 2.3 필드 타입별 가이드

#### CharField

```python
name = models.CharField(
    max_length=255,
    verbose_name=_("이름")
)

# 선택지가 있는 경우
status = models.CharField(
    max_length=20,
    choices=STATUS_CHOICES,
    default="active",
    verbose_name=_("상태")
)
```

#### TextField

```python
description = models.TextField(
    blank=True, null=True,
    verbose_name=_("설명")
)
```

#### DecimalField (가격, 금액)

```python
price = models.DecimalField(
    max_digits=12,      # 전체 자릿수
    decimal_places=2,   # 소수점 이하 자릿수
    null=True, blank=True,
    verbose_name=_("가격")
)
```

#### ImageField/FileField

```python
thumbnail = models.ImageField(
    upload_to="thumbnails/%Y/%m/",  # 연/월별 폴더 분리
    blank=True, null=True,
    verbose_name=_("썸네일")
)
```

#### DateTime 필드

```python
created_at = models.DateTimeField(
    auto_now_add=True,
    verbose_name=_("생성일")
)

updated_at = models.DateTimeField(
    auto_now=True,
    verbose_name=_("수정일")
)
```

## 3. 관계 필드 가이드

### 3.1 ForeignKey

```python
# 기본 패턴
category = models.ForeignKey(
    Category,
    on_delete=models.CASCADE,     # 또는 PROTECT, SET_NULL
    related_name="courses",       # 역참조 이름
    verbose_name=_("카테고리")
)

# User 모델 참조
user = models.ForeignKey(
    User,
    on_delete=models.CASCADE,
    related_name="user_courses",
    verbose_name=_("사용자")
)
```

### 3.2 on_delete 옵션 선택 가이드

- `CASCADE`: 참조 객체 삭제 시 함께 삭제
- `PROTECT`: 참조 객체 삭제 방지
- `SET_NULL`: 참조 객체 삭제 시 NULL로 설정 (null=True 필수)
- `SET_DEFAULT`: 기본값으로 설정

## 4. 메서드 정의

### 4.1 필수 메서드

```python
def __str__(self):
    return self.title  # 또는 의미있는 문자열 표현

def get_absolute_url(self):
    from django.urls import reverse
    return reverse('course_detail', kwargs={'pk': self.pk})
```

### 4.2 커스텀 메서드 예시

```python
@property
def is_published(self):
    return self.status == 'published'

def get_display_price(self):
    if self.price:
        return f"{self.price:,} {self.currency}"
    return "무료"
```

## 5. Meta 클래스

### 5.1 기본 Meta 옵션

```python
class Meta:
    db_table = "course"                    # 테이블명 명시
    verbose_name = _("코스")               # 단수형 표시명
    verbose_name_plural = _("코스")        # 복수형 표시명
    ordering = ["-created_at"]            # 기본 정렬

    # 추가 옵션들
    unique_together = [["field1", "field2"]]  # 복합 유니크
    indexes = [
        models.Index(fields=["status", "created_at"]),
    ]
```

## 6. 전체 템플릿

```python
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from your_app.models.category import Category

User = get_user_model()


class Course(models.Model):
    # 상수 정의
    LEVEL_CHOICES = [
        ("beginner", _("초급")),
        ("intermediate", _("중급")),
        ("advanced", _("고급")),
    ]

    STATUS_CHOICES = [
        ("draft", _("초안")),
        ("published", _("게시됨")),
        ("archived", _("보관됨")),
    ]

    # 필드 정의 (순서대로)
    # 1. ID/식별자 필드
    course_id = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_("코스 ID")
    )

    # 2. Foreign Key 필드
    instructor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="courses",
        verbose_name=_("강사")
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="courses",
        verbose_name=_("카테고리")
    )

    # 3. 필수 데이터 필드
    title = models.CharField(
        max_length=255,
        verbose_name=_("제목")
    )

    level = models.CharField(
        max_length=20,
        choices=LEVEL_CHOICES,
        verbose_name=_("난이도")
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft",
        verbose_name=_("상태")
    )

    # 4. 선택사항 필드
    description = models.TextField(
        blank=True, null=True,
        verbose_name=_("설명")
    )

    thumbnail = models.ImageField(
        upload_to="course_thumbnails/%Y/%m/",
        blank=True, null=True,
        verbose_name=_("썸네일")
    )

    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True, blank=True,
        verbose_name=_("가격")
    )

    currency = models.CharField(
        max_length=10,
        default="KRW",
        verbose_name=_("통화")
    )

    # 5. 타임스탬프 필드
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("생성일")
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("수정일")
    )

    # 메서드 정의
    def __str__(self):
        return self.title

    @property
    def is_published(self):
        return self.status == "published"

    def get_display_price(self):
        if self.price:
            return f"{self.price:,} {self.currency}"
        return "무료"

    class Meta:
        db_table = "course"
        verbose_name = _("코스")
        verbose_name_plural = _("코스")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["category", "level"]),
        ]
```

## 7. 체크리스트

### 모델 작성 완료 후 확인사항

- [ ] 모든 필드에 `verbose_name` 설정
- [ ] ForeignKey에 적절한 `on_delete` 옵션 설정
- [ ] `related_name` 설정으로 역참조 이름 명시
- [ ] 필요한 곳에 `blank=True, null=True` 설정
- [ ] `__str__` 메서드 구현
- [ ] Meta 클래스에 필수 옵션들 설정
- [ ] 마이그레이션 파일 생성 및 적용
- [ ] Admin 등록 (필요시)

이 가이드라인을 따르면 일관성 있고 유지보수하기 쉬운 Django 모델을 작성할 수 있습니다.

## 8. API 응답 및 요청 처리 가이드

### 8.1 네이밍 컨벤션 원칙

- **백엔드 내부**: 모든 곳에서 `snake_case` 사용
  - 모델 필드, 시리얼라이저 필드, 뷰 로직, DB 컬럼명
- **API 응답/요청**: `camelCase` 사용
  - 프론트엔드와의 데이터 교환은 camelCase로 통일

### 8.2 시리얼라이저에서 camelCase 변환

#### 기본 변환 함수

```python
import re

def to_camel_case(snake_str):
    """snake_case를 camelCase로 변환"""
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])

def to_snake_case(camel_str):
    """camelCase를 snake_case로 변환"""
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', camel_str)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
```

#### Base Serializer 클래스

```python
from rest_framework import serializers

class CamelCaseSerializer(serializers.ModelSerializer):
    """camelCase 자동 변환을 지원하는 기본 시리얼라이저"""

    def to_representation(self, instance):
        """응답 시 snake_case -> camelCase 변환"""
        data = super().to_representation(instance)
        return {to_camel_case(key): value for key, value in data.items()}

    def to_internal_value(self, data):
        """요청 시 camelCase -> snake_case 변환"""
        snake_case_data = {to_snake_case(key): value for key, value in data.items()}
        return super().to_internal_value(snake_case_data)
```

#### 사용 예시

```python
from django.contrib.auth import get_user_model
from .base import CamelCaseSerializer

User = get_user_model()

class UserSerializer(CamelCaseSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'phone_number', 'real_name', 'created_at']

# API 응답 예시:
# 내부 필드: phone_number, real_name, created_at
# API 응답: phoneNumber, realName, createdAt
```

### 8.3 뷰에서의 처리

#### APIView 클래스

```python
from rest_framework.views import APIView
from rest_framework.response import Response

class CourseListAPIView(APIView):
    def get(self, request):
        courses = Course.objects.all()
        serializer = CourseSerializer(courses, many=True)
        # 시리얼라이저에서 자동으로 camelCase 변환됨
        return Response(serializer.data)

    def post(self, request):
        # 요청 데이터는 camelCase로 들어오지만
        # 시리얼라이저에서 자동으로 snake_case로 변환됨
        serializer = CourseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
```

### 8.4 프론트엔드 요청/응답 예시

#### 요청 (프론트 → 백엔드)

```javascript
// 프론트엔드에서 보내는 데이터 (camelCase)
const courseData = {
  courseId: "COURSE_001",
  instructorName: "김강사",
  categoryId: 1,
  createdAt: "2025-01-01T00:00:00Z",
};

// 백엔드에서 자동으로 snake_case로 변환되어 처리됨
// course_id, instructor_name, category_id, created_at
```

#### 응답 (백엔드 → 프론트)

```json
{
  "courseId": "COURSE_001",
  "instructorName": "김강사",
  "categoryId": 1,
  "createdAt": "2025-01-01T00:00:00Z"
}
```

### 8.5 체크리스트

#### API 개발 시 확인사항

- [ ] 모든 시리얼라이저는 `CamelCaseSerializer`를 상속받아 구현
- [ ] 모델 필드명은 snake_case로 작성
- [ ] API 문서(Swagger)에서 camelCase로 표시되는지 확인
- [ ] 프론트엔드 개발자와 필드명 컨벤션 공유
- [ ] 중첩 객체나 배열에서도 변환이 올바르게 작동하는지 테스트

이 가이드라인을 따르면 백엔드는 Python/Django 컨벤션을 유지하면서, 프론트엔드는 JavaScript 컨벤션에 맞는 자연스러운 API를 제공할 수 있습니다.

## 9. Django Unfold Admin 작성 가이드

### 9.1 기본 구조

Django Unfold를 사용한 Admin 클래스는 다음과 같은 구조로 작성합니다:

```python
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin
from unfold.decorators import action

from your_app.models.your_model import YourModel

@admin.register(YourModel)
class YourModelAdmin(ModelAdmin):
    # 기본 설정
    list_display = []
    list_filter = []
    search_fields = []
    ordering = []
    readonly_fields = []

    # Unfold 특화 설정
    fieldsets = []
    actions = []

    # 성능 최적화
    list_select_related = []

    # 커스텀 메서드들
    def custom_display_method(self, obj):
        pass
```

### 9.2 Admin 폴더 구조

Admin 클래스들을 별도 폴더로 관리합니다:

```
your_app/
├── admins/
│   ├── __init__.py        # 자동 import
│   ├── model1.py          # Model1Admin
│   ├── model2.py          # Model2Admin
│   └── ...
└── admin.py               # admins 폴더 import
```

#### **init**.py (자동 import)

```python
import os
import importlib

current_dir = os.path.dirname(__file__)

for filename in os.listdir(current_dir):
    if filename.endswith(".py") and filename != "__init__.py":
        module_name = f"{__name__}.{filename[:-3]}"
        importlib.import_module(module_name)
```

#### admin.py

```python
from your_app.admins import *
```

### 9.3 기본 Admin 템플릿

#### 단순 모델 Admin

```python
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin

from your_app.models.category import Category

@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ["name", "description", "created_at", "updated_at"]
    list_filter = ["created_at", "updated_at"]
    search_fields = ["name", "description"]
    ordering = ["-created_at"]
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = [
        (
            _("기본 정보"),
            {
                "fields": [
                    "name",
                    "description",
                ]
            },
        ),
        (
            _("타임스탬프"),
            {
                "fields": [
                    "created_at",
                    "updated_at",
                ],
                "classes": ["collapse"],
            },
        ),
    ]

    # Unfold 추가 설정
    list_per_page = 20
    search_help_text = _("이름이나 설명으로 검색할 수 있습니다.")
```

#### 복잡한 모델 Admin

```python
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin
from unfold.decorators import action

from your_app.models.course import Course

@admin.register(Course)
class CourseAdmin(ModelAdmin):
    list_display = [
        "course_id",
        "title",
        "instructor_name",
        "category",
        "status",
        "price_display",
        "created_at"
    ]
    list_filter = [
        "status",
        "category",
        "created_at",
    ]
    search_fields = [
        "course_id",
        "title",
        "instructor_name",
        "description",
    ]
    ordering = ["-created_at"]
    readonly_fields = ["created_at", "updated_at", "thumbnail_preview"]
    list_select_related = ["instructor", "category"]
    actions = ["publish_courses", "unpublish_courses"]

    fieldsets = [
        (
            _("기본 정보"),
            {
                "fields": [
                    "course_id",
                    "title",
                    "description",
                    "status",
                ]
            },
        ),
        (
            _("관계"),
            {
                "fields": [
                    "instructor",
                    "category",
                ]
            },
        ),
        (
            _("미디어"),
            {
                "fields": [
                    "thumbnail",
                    "thumbnail_preview",
                ],
                "classes": ["collapse"],
            },
        ),
        (
            _("타임스탬프"),
            {
                "fields": [
                    "created_at",
                    "updated_at",
                ],
                "classes": ["collapse"],
            },
        ),
    ]

    def price_display(self, obj):
        """가격 표시 개선"""
        if obj.price:
            return f"{obj.price:,.0f} {obj.currency}"
        return _("무료")
    price_display.short_description = _("가격")

    def thumbnail_preview(self, obj):
        """썸네일 미리보기"""
        if obj.thumbnail:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 150px;" />',
                obj.thumbnail.url
            )
        return _("이미지 없음")
    thumbnail_preview.short_description = _("썸네일 미리보기")

    @action(description=_("선택된 항목을 게시 상태로 변경"))
    def publish_courses(self, request, queryset):
        updated = queryset.update(status="Published")
        self.message_user(request, f"{updated}개 항목이 게시되었습니다.")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("instructor", "category")
```

### 9.4 주요 기능들

#### list_display 개선

- 관계 필드 표시: `"category"`, `"instructor"`
- 커스텀 메서드: `"price_display"`, `"status_badge"`
- 타임스탬프: `"created_at"`, `"updated_at"`

#### 검색 및 필터링

```python
search_fields = [
    "title",
    "description",
    "related_model__field",  # 관계 필드 검색
]

list_filter = [
    "status",
    "category",
    "created_at",
    "updated_at",
]
```

#### 성능 최적화

```python
list_select_related = ["category", "instructor"]  # ForeignKey
list_prefetch_related = ["tags", "sections"]      # ManyToMany, reverse FK

def get_queryset(self, request):
    qs = super().get_queryset(request)
    return qs.select_related("category", "instructor")
```

#### 커스텀 액션

```python
@action(description=_("선택된 항목을 활성화"))
def activate_items(self, request, queryset):
    updated = queryset.update(is_active=True)
    self.message_user(request, f"{updated}개 항목이 활성화되었습니다.")
```

### 9.5 체크리스트

#### Admin 작성 완료 후 확인사항

- [ ] `@admin.register(Model)` 데코레이터 추가
- [ ] `ModelAdmin` 상속 (unfold.admin.ModelAdmin)
- [ ] `list_display`에 주요 필드들 설정
- [ ] `search_fields`로 검색 기능 제공
- [ ] `list_filter`로 필터링 기능 제공
- [ ] `readonly_fields`에 자동 생성 필드들 설정
- [ ] `fieldsets`으로 필드 그룹화
- [ ] 성능 최적화 (`select_related`, `prefetch_related`)
- [ ] 커스텀 표시 메서드들 구현
- [ ] 필요시 커스텀 액션 추가

이 가이드라인을 따르면 Django Unfold를 활용한 현대적이고 사용자 친화적인 관리자 인터페이스를 구축할 수 있습니다.

## 10. DRF Spectacular API 문서화 가이드

### 10.1 기본 설정

#### settings.py 설정

```python
INSTALLED_APPS = [
    # ...
    'drf_spectacular',
    'drf_spectacular_sidecar',
]

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

SPECTACULAR_SETTINGS = {
    'TITLE': '프로젝트 API',
    'DESCRIPTION': 'API 문서',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX': r'/api/v[0-9]',
    'SWAGGER_UI_DIST': 'SIDECAR',
    'SWAGGER_UI_FAVICON_HREF': 'SIDECAR',
    'REDOC_DIST': 'SIDECAR',
    # 태그 설정
    'TAGS': [
        {'name': 'users', 'description': '사용자 관리'},
        {'name': 'courses', 'description': '코스 관리'},
        {'name': 'auth', 'description': '인증/인가'},
    ],
}
```

#### urls.py 설정

```python
from django.urls import path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    # API 스키마
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Swagger UI
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    # ReDoc
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
```

### 10.2 ViewSet 문서화

#### 기본 ViewSet 문서화

```python
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from rest_framework import viewsets
from rest_framework.decorators import action

@extend_schema_view(
    list=extend_schema(
        summary="코스 목록 조회",
        description="게시된 코스 목록을 조회합니다.",
        tags=['courses'],
    ),
    retrieve=extend_schema(
        summary="코스 상세 조회",
        description="특정 코스의 상세 정보를 조회합니다.",
        tags=['courses'],
    ),
    create=extend_schema(
        summary="코스 생성",
        description="새로운 코스를 생성합니다.",
        tags=['courses'],
    ),
    update=extend_schema(
        summary="코스 수정",
        description="기존 코스 정보를 수정합니다.",
        tags=['courses'],
    ),
    partial_update=extend_schema(
        summary="코스 부분 수정",
        description="코스 정보를 부분적으로 수정합니다.",
        tags=['courses'],
    ),
    destroy=extend_schema(
        summary="코스 삭제",
        description="코스를 삭제합니다.",
        tags=['courses'],
    ),
)
class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    
    @extend_schema(
        summary="코스 게시",
        description="선택한 코스를 게시 상태로 변경합니다.",
        tags=['courses'],
        request=None,
        responses={200: CourseSerializer(many=True)},
    )
    @action(detail=False, methods=['post'])
    def publish(self, request):
        # 구현 코드
        pass
```

#### 쿼리 파라미터 문서화

```python
@extend_schema(
    summary="코스 목록 조회",
    description="다양한 필터 옵션으로 코스를 조회합니다.",
    tags=['courses'],
    parameters=[
        OpenApiParameter(
            name='category_id',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description='카테고리 ID로 필터링',
            required=False,
        ),
        OpenApiParameter(
            name='instructor_id',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description='강사 ID로 필터링',
            required=False,
        ),
        OpenApiParameter(
            name='min_price',
            type=OpenApiTypes.FLOAT,
            location=OpenApiParameter.QUERY,
            description='최소 가격',
            required=False,
        ),
        OpenApiParameter(
            name='max_price',
            type=OpenApiTypes.FLOAT,
            location=OpenApiParameter.QUERY,
            description='최대 가격',
            required=False,
        ),
        OpenApiParameter(
            name='is_free',
            type=OpenApiTypes.BOOL,
            location=OpenApiParameter.QUERY,
            description='무료 코스만 조회',
            required=False,
        ),
        OpenApiParameter(
            name='search',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='제목, 설명으로 검색',
            required=False,
        ),
        OpenApiParameter(
            name='ordering',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='정렬 기준 (created_at, -created_at, price, -price)',
            required=False,
        ),
    ],
)
def list(self, request, *args, **kwargs):
    return super().list(request, *args, **kwargs)
```

### 10.3 Serializer 문서화

#### 기본 Serializer 문서화

```python
from drf_spectacular.utils import extend_schema_field, extend_schema_serializer
from rest_framework import serializers

@extend_schema_serializer(
    examples=[
        {
            'name': '코스 예시',
            'value': {
                'courseId': 'COURSE_001',
                'title': 'Django 마스터하기',
                'description': 'Django 완벽 가이드',
                'price': 99000,
                'currency': 'KRW',
            }
        }
    ]
)
class CourseSerializer(serializers.ModelSerializer):
    # 커스텀 필드 문서화
    instructor_name = serializers.CharField(
        source='instructor.get_full_name',
        read_only=True,
        help_text='강사 이름'
    )
    
    @extend_schema_field(OpenApiTypes.STR)
    def get_display_price(self, obj):
        """가격 표시 형식"""
        if obj.price:
            return f"{obj.price:,} {obj.currency}"
        return "무료"
    
    class Meta:
        model = Course
        fields = [
            'id',
            'course_id',
            'title',
            'description',
            'instructor_name',
            'category',
            'price',
            'currency',
            'display_price',
        ]
        read_only_fields = ['id', 'instructor_name', 'display_price']
```

#### 중첩 Serializer 문서화

```python
class SectionSerializer(serializers.ModelSerializer):
    chapters = ChapterSerializer(many=True, read_only=True)
    
    class Meta:
        model = Section
        fields = ['id', 'title', 'order', 'chapters']

@extend_schema_serializer(
    examples=[
        {
            'name': '상세 코스 예시',
            'value': {
                'courseId': 'COURSE_001',
                'title': 'Django 마스터하기',
                'sections': [
                    {
                        'id': 1,
                        'title': '섹션 1',
                        'chapters': [
                            {'id': 1, 'title': '챕터 1'},
                            {'id': 2, 'title': '챕터 2'},
                        ]
                    }
                ]
            }
        }
    ]
)
class CourseDetailSerializer(serializers.ModelSerializer):
    sections = SectionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Course
        fields = ['id', 'course_id', 'title', 'sections']
```

### 10.4 APIView 문서화

#### 기본 APIView 문서화

```python
from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.response import Response

class CourseListAPIView(APIView):
    @extend_schema(
        summary="코스 목록 조회",
        description="게시된 코스 목록을 조회합니다.",
        tags=['courses'],
        parameters=[
            OpenApiParameter(
                name='category_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='카테고리 ID',
            ),
        ],
        responses={
            200: CourseListSerializer(many=True),
            400: OpenApiTypes.OBJECT,
        },
    )
    def get(self, request):
        courses = Course.objects.filter(status='published')
        serializer = CourseListSerializer(courses, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="코스 생성",
        description="새로운 코스를 생성합니다.",
        tags=['courses'],
        request=CourseCreateSerializer,
        responses={
            201: CourseSerializer,
            400: OpenApiTypes.OBJECT,
        },
    )
    def post(self, request):
        serializer = CourseCreateSerializer(data=request.data)
        if serializer.is_valid():
            course = serializer.save()
            return Response(
                CourseSerializer(course).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
```

### 10.5 응답 예시 커스터마이징

#### 성공/에러 응답 예시

```python
from drf_spectacular.utils import OpenApiExample

@extend_schema(
    summary="코스 생성",
    description="새로운 코스를 생성합니다.",
    tags=['courses'],
    request=CourseCreateSerializer,
    responses={
        201: CourseSerializer,
        400: OpenApiTypes.OBJECT,
    },
    examples=[
        OpenApiExample(
            '성공 예시',
            value={
                'courseId': 'COURSE_001',
                'title': 'Django 마스터하기',
                'status': 'published',
            },
            response_only=True,
            status_codes=['201'],
        ),
        OpenApiExample(
            '에러 예시',
            value={
                'title': ['이 필드는 필수입니다.'],
                'price': ['유효한 숫자를 입력하세요.'],
            },
            response_only=True,
            status_codes=['400'],
        ),
    ],
)
def post(self, request):
    # 구현 코드
    pass
```

### 10.6 Base View 패턴

#### BaseAPIView 및 상속형 뷰

```python
from rest_framework import generics
from drf_spectacular.utils import extend_schema

class BaseAPIView:
    """모든 API View의 기본 클래스"""
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

class BaseListAPIView(BaseAPIView, generics.ListAPIView):
    """목록 조회 기본 클래스"""
    pass

class BaseDetailAPIView(BaseAPIView, generics.RetrieveAPIView):
    """상세 조회 기본 클래스"""
    pass

class BaseCreateAPIView(BaseAPIView, generics.CreateAPIView):
    """생성 기본 클래스"""
    pass

class BaseUpdateAPIView(BaseAPIView, generics.UpdateAPIView):
    """수정 기본 클래스"""
    pass

class BaseDestroyAPIView(BaseAPIView, generics.DestroyAPIView):
    """삭제 기본 클래스"""
    pass
```

#### 실제 사용 예시

```python
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.permissions import AllowAny

class CourseListAPIView(BaseListAPIView):
    serializer_class = CourseListSerializer
    permission_classes = [AllowAny]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ['category', 'instructor', 'level', 'status']
    search_fields = ['title', 'description', 'course_id']
    ordering_fields = ['created_at', 'updated_at', 'title', 'price']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return Course.objects.select_related(
            'category',
            'instructor'
        ).filter(status='published')
    
    @extend_schema(
        summary="코스 목록 조회",
        description="카테고리, 강사, 가격 등으로 필터링하여 코스 목록을 조회합니다.",
        tags=['courses'],
        parameters=[
            OpenApiParameter(
                name='category',
                type=OpenApiTypes.INT,
                description='카테고리 ID',
            ),
            OpenApiParameter(
                name='instructor',
                type=OpenApiTypes.INT,
                description='강사 ID',
            ),
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                description='검색어 (제목, 설명)',
            ),
            OpenApiParameter(
                name='ordering',
                type=OpenApiTypes.STR,
                description='정렬 (created_at, -created_at, title, price)',
            ),
        ],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class CourseDetailAPIView(BaseDetailAPIView):
    serializer_class = CourseDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = 'course_id'
    
    def get_queryset(self):
        return Course.objects.select_related(
            'category',
            'instructor'
        ).prefetch_related(
            'sections',
            'sections__chapters'
        ).filter(status='published')
    
    @extend_schema(
        summary="코스 상세 조회",
        description="코스 ID로 특정 코스의 상세 정보를 조회합니다.",
        tags=['courses'],
        parameters=[
            OpenApiParameter(
                name='course_id',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                description='코스 ID',
            ),
        ],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
```

### 10.7 체크리스트

#### API 문서화 완료 후 확인사항

- [ ] `@extend_schema` 또는 `@extend_schema_view` 데코레이터 추가
- [ ] `summary`와 `description` 작성
- [ ] 적절한 `tags` 설정
- [ ] 쿼리 파라미터 문서화 (`OpenApiParameter`)
- [ ] 요청/응답 예시 추가 (`OpenApiExample`)
- [ ] Serializer에 `help_text` 추가
- [ ] 커스텀 필드에 `@extend_schema_field` 추가
- [ ] 응답 상태 코드별 예시 작성
- [ ] BaseAPIView 패턴 준수
- [ ] 성능 최적화 (select_related, prefetch_related)
- [ ] Swagger UI에서 실제 동작 테스트

이 가이드라인을 따르면 DRF Spectacular를 활용한 명확하고 사용하기 쉬운 API 문서를 작성할 수 있습니다.
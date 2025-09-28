from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.viewsets import ModelViewSet

from ...models import User
from ...serializers import UserListSerializer


@extend_schema_view(
    list=extend_schema(
        tags=["external-user"],
        operation_id="external_users_list",
        summary="[외부] 공개 사용자 정보",
        description="""
        **외부 연동용** - 제한된 사용자 정보를 제공합니다.
        
        ### 기능
        - 활성 사용자만 조회
        - 기본 정보만 제공 (보안상 제한)
        - 조회만 가능 (생성/수정/삭제 불가)
        """,
    ),
    retrieve=extend_schema(
        tags=["external-user"],
        operation_id="external_users_detail",
        summary="[외부] 사용자 기본 정보 조회",
        description="""
        **외부 연동용** - 특정 사용자의 기본 정보만 조회합니다.
        """,
    ),
)
class ExternalUserViewSet(ModelViewSet):
    """
    ## 🌐 외부 연동용 사용자 ViewSet

    외부 시스템 연동을 위한 제한된 사용자 정보를 제공합니다.

    ### 🔒 접근 제한
    - 조회만 가능 (GET 메서드만 허용)
    - 활성 사용자만 노출
    - 기본 정보만 제공
    """

    queryset = User.objects.filter(is_active=True)
    serializer_class = UserListSerializer
    http_method_names = ["get"]  # 조회만 허용

from django.views.generic import TemplateView
from rest_framework import viewsets, permissions, pagination
from rest_framework.schemas import openapi
from rest_framework.schemas.views import SchemaView
from rest_framework.settings import api_settings
from rest_framework_extensions.mixins import NestedViewSetMixin

from grades.models import Course, Grade, Tag, Report, CourseTag

from .filters import CourseFilter, GradeFilter
from .permissions import (
    DjangoModelPermissionOrAnonCreateOnly,
    IsAuthenticatedOrReadOnlyOrIsAdminUserOrOwnerEdit,
)
from .serializers import (
    CourseSerializer,
    GradeSerializer,
    TagSerializer,
    ReportSerializer,
    CourseTagSerializer,
)


class CourseViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    lookup_field = "code"
    serializer_class = CourseSerializer
    queryset = Course.objects.all()
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)
    pagination_class = pagination.LimitOffsetPagination
    filterset_class = CourseFilter
    ordering_fields = (
        "watson_rank",
        "norwegian_name",
        "short_name",
        "code",
        "english_name",
        "average",
        "attendee_count",
    )


class GradeViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    lookup_field = "semester_code"
    serializer_class = GradeSerializer
    queryset = Grade.objects.all()
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)
    pagination_class = pagination.LimitOffsetPagination
    filterset_class = GradeFilter


class CourseTagViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    lookup_field = "tag__tag"
    serializer_class = CourseTagSerializer
    queryset = CourseTag.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnlyOrIsAdminUserOrOwnerEdit,)
    pagination_class = pagination.LimitOffsetPagination

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(created_by=user)


class TagViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    lookup_field = "tag"
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)
    pagination_class = pagination.LimitOffsetPagination


class ReportViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    serializer_class = ReportSerializer
    queryset = Report.objects.all()
    permission_classes = (DjangoModelPermissionOrAnonCreateOnly,)
    pagination_class = pagination.LimitOffsetPagination


class SwaggerUIView(TemplateView):
    template_name = "swagger-ui.html"
    extra_context = {"schema_url": "openapi-schema"}


class OpenAPISchemaView(SchemaView):
    authentication_classes = api_settings.DEFAULT_AUTHENTICATION_CLASSES
    permission_classes = api_settings.DEFAULT_PERMISSION_CLASSES
    schema_generator = openapi.SchemaGenerator(
        title="Gradestats API",
        description="Rest API for grades.no",
        version="2.0.0",
        urlconf="grades_api_v2.urls",
        url="/api/v2",
    )
    public = True

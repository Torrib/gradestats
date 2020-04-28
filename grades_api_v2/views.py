from django.views.generic import TemplateView
from rest_framework import viewsets, permissions, pagination
from rest_framework.schemas import openapi
from rest_framework.schemas.views import SchemaView
from rest_framework.settings import api_settings
from rest_framework_extensions.mixins import NestedViewSetMixin

from grades.models import Course, Grade

from .filters import CourseFilter, GradeFilter
from .serializers import CourseSerializer, GradeSerializer


class CourseViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    lookup_field = "code"
    serializer_class = CourseSerializer
    queryset = Course.objects.all()
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)
    pagination_class = pagination.LimitOffsetPagination
    filterset_class = CourseFilter


class GradeViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    lookup_field = "semester_code"
    serializer_class = GradeSerializer
    queryset = Grade.objects.all()
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)
    pagination_class = pagination.LimitOffsetPagination
    filterset_class = GradeFilter


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

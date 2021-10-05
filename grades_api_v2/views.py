from django.contrib.auth.models import User
from django.views.generic import TemplateView
from rest_framework import viewsets, permissions, pagination, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.schemas import openapi
from rest_framework.schemas.views import SchemaView
from rest_framework.settings import api_settings
from rest_framework_extensions.mixins import NestedViewSetMixin

from clients.course_pages import CoursePagesClient
from clients.karstat import KarstatGradeClient
from clients.nsd import NSDGradeClient
from clients.tia import TIACourseClient, TIADepartmentClient, TIAFacultyClient
from grades.models import (
    Course,
    Grade,
    Tag,
    Favourite,
    Report,
    CourseTag,
    Faculty,
    Department,
)

from .filters import CourseFilter, GradeFilter
from .permissions import (
    DjangoModelPermissionOrAnonCreateOnly,
    IsAuthenticatedOrReadOnlyOrIsAdminUserOrOwnerEdit,
    UserViewPermission,
    IsAdminUserOrReadOnly,
    IsFavouriteOwnerPermission,
)
from .serializers import (
    CourseSerializer,
    GradeSerializer,
    TagSerializer,
    FavouriteSerializer,
    ReportSerializer,
    CourseTagSerializer,
    FacultySerializer,
    DepartmentSerializer,
    UserSerializer,
    TIAObjectListRefreshSerializer,
    KarstatGradeReportSerializer,
    NSDGradeReportSerializer,
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

    @action(
        url_path="refresh-course-pages",
        detail=True,
        methods=["POST"],
        permission_classes=(permissions.IsAdminUser,),
    )
    def refresh_course_pages(self, request, *args, **kwargs):
        course = self.get_object()
        client = CoursePagesClient()
        client.update_course(course_code=course.code)
        course.refresh_from_db()
        serializer = self.get_serializer(instance=course)
        return Response(status=status.HTTP_200_OK, data=serializer.data)


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


class FavouritesViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    serializer_class = FavouriteSerializer
    queryset = Favourite.objects.all()
    permission_classes = (permissions.IsAdminUser,)
    pagination_class = pagination.LimitOffsetPagination


class ReportViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    serializer_class = ReportSerializer
    queryset = Report.objects.all()
    permission_classes = (DjangoModelPermissionOrAnonCreateOnly,)
    pagination_class = pagination.LimitOffsetPagination


class UserViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    lookup_field = "username"
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (UserViewPermission,)
    pagination_class = pagination.LimitOffsetPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        user: User = self.request.user
        if not user.is_staff:
            return queryset.filter(pk=user.id)
        return queryset


class UserCourseTagViewSet(CourseTagViewSet):
    permission_classes = (
        permissions.IsAuthenticated,
        IsAdminUserOrReadOnly,
    )

    def get_queryset(self):
        queryset = super().get_queryset()
        user: User = self.request.user
        if not user.is_staff:
            return queryset.filter(created_by=user.id)
        return queryset


class UserFavouritesViewSet(
    NestedViewSetMixin,
    viewsets.GenericViewSet,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
):
    serializer_class = FavouriteSerializer
    queryset = Favourite.objects.all()
    permission_classes = (IsFavouriteOwnerPermission,)
    pagination_class = pagination.LimitOffsetPagination

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user)

    def get_queryset(self):
        queryset = super().get_queryset()
        user: User = self.request.user
        return queryset.filter(user=user.id)


class FacultyViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    serializer_class = FacultySerializer
    queryset = Faculty.objects.all()
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)
    pagination_class = pagination.LimitOffsetPagination


class DepartmentViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    serializer_class = DepartmentSerializer
    queryset = Department.objects.all()
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)
    pagination_class = pagination.LimitOffsetPagination


def scrape_list_refresh_action(url_path: str):
    return action(
        url_path=url_path,
        detail=False,
        methods=["POST"],
        serializer_class=TIAObjectListRefreshSerializer,
        permission_classes=(permissions.IsAdminUser,),
    )


class TIAScraperViewSet(viewsets.GenericViewSet):
    def _refresh_object_list(
        self, request, object_serializer_class, scraper_client_class
    ):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        client = scraper_client_class()
        client.login(
            username=data.get("username"), password=data.get("password"),
        )
        objects = client.refresh_objects(
            limit=data.get("limit"), skip=data.get("skip"),
        )
        objects_serializer = object_serializer_class(instance=objects, many=True)
        return Response(status=status.HTTP_200_OK, data=objects_serializer.data)

    @scrape_list_refresh_action(url_path="refresh-courses")
    def refresh_courses(self, request, *args, **kwargs):
        return self._refresh_object_list(
            request,
            object_serializer_class=CourseSerializer,
            scraper_client_class=TIACourseClient,
        )

    @scrape_list_refresh_action(url_path="refresh-faculties")
    def refresh_faculties(self, request, *args, **kwargs):
        return self._refresh_object_list(
            request,
            object_serializer_class=FacultySerializer,
            scraper_client_class=TIAFacultyClient,
        )

    @scrape_list_refresh_action(url_path="refresh-departments")
    def refresh_departments(self, request, *args, **kwargs):
        return self._refresh_object_list(
            request,
            object_serializer_class=DepartmentSerializer,
            scraper_client_class=TIADepartmentClient,
        )


class KarstatScraperViewSet(viewsets.GenericViewSet):
    @action(
        url_path="grade-report",
        detail=False,
        methods=["POST"],
        serializer_class=KarstatGradeReportSerializer,
        permission_classes=(permissions.IsAdminUser,),
    )
    def grade_report(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        department = Department.objects.get(pk=data.get("department"))
        client = KarstatGradeClient()
        client.login(
            username=data.get("username"), password=data.get("password"),
        )
        grades = client.update_grade_stats(
            department=department, year=data.get("year"), semester=data.get("semester"),
        )
        grades_serializer = GradeSerializer(instance=grades, many=True)
        return Response(status=status.HTTP_200_OK, data=grades_serializer.data)


class NSDScraperViewSet(viewsets.GenericViewSet):
    @action(
        url_path="grade-report",
        detail=False,
        methods=["POST"],
        serializer_class=NSDGradeReportSerializer,
        permission_classes=(permissions.AllowAny,),
    )
    def grade_report(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        client = NSDGradeClient()
        grade = client.update_grade(
            course_code=data.get("course"),
            year=data.get("year"),
            semester=data.get("semester"),
        )
        if not grade:
            return Response(status=status.HTTP_404_NOT_FOUND)
        grade_serializer = GradeSerializer(instance=grade)
        return Response(status=status.HTTP_200_OK, data=grade_serializer.data)


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

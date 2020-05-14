from django.urls import path

from grades_api_v2 import views

from .router import SharedAPIRootRouter

urlpatterns = [
    path("docs/", views.SwaggerUIView.as_view(), name="swagger-ui"),
    path("openapi-schema", views.OpenAPISchemaView.as_view(), name="openapi-schema"),
]

router = SharedAPIRootRouter()

CoursesRouter = router.register("courses", views.CourseViewSet, basename="courses")
CourseGradesRouter = CoursesRouter.register(
    "grades",
    views.GradeViewSet,
    basename="course-grades",
    parents_query_lookups=["course__code"],
)
CourseTagsRouter = CoursesRouter.register(
    "tags",
    views.CourseTagViewSet,
    basename="course-tags",
    parents_query_lookups=["course__code"],
)
TagRouter = router.register("tags", views.TagViewSet, basename="tags")
ReportRouter = router.register("reports", views.ReportViewSet, basename="reports")

urlpatterns += router.urls

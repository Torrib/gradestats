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
FacultiesRouter = router.register(
    "faculties", views.FacultyViewSet, basename="faculties"
)
DepartmentsRouter = router.register(
    "departments", views.DepartmentViewSet, basename="departments"
)
UserRouter = router.register("users", views.UserViewSet, basename="users")
UserCourseTagsRouter = UserRouter.register(
    "tags",
    views.UserCourseTagViewSet,
    basename="user-tags",
    parents_query_lookups=["created_by"],
)
TIAScraperRouter = router.register(
    "scrapers/tia", views.TIAScraperViewSet, basename="scrapers-tia"
)
KarstatScraperRouter = router.register(
    "scrapers/karstat", views.KarstatScraperViewSet, basename="scrapers-karstat"
)
NSDScraperRouter = router.register(
    "scrapers/nsd", views.NSDScraperViewSet, basename="scrapers-nsd"
)

urlpatterns += router.urls

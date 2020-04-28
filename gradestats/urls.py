from django.conf.urls import include
from django.contrib import admin
from django.urls import path

from grades.views import *
from grades_api.views import *
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.routers import SimpleRouter
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("", index, name="index"),
    path("index/", index, name="index"),
    path("course/", index, name="index"),
    path("course/<course_code>/", course, name="course",),
    path("course/<course_code>/tags/add/", add_tag, name="add_tag",),
    path("course/<course_code>/grades/", get_grades, name="get_grades",),
    path("search/", search, name="search"),
    path("about/", about, name="about"),
    path("report/", report, name="report"),
    path("api/", api, name="api"),
    path("admin/", admin.site.urls),
]

router = SimpleRouter(trailing_slash=False)
router.register("api/courses", CourseViewSet)  # Create routes for Courses
router.register(
    r"api/courses/(?P<course_code>\w+)/grades", GradeViewSet,
)
router.register(
    r"api/courses/(?P<course_code>\w+)/grades/", GradeViewSet,
)
router.register("api/index", CourseIndexViewSet)
router.register("api/typeahead/course", CourseTypeaheadViewSet)

urlpatterns += format_suffix_patterns(router.urls, allowed=["json"])
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if "grades_api_v2" in settings.INSTALLED_APPS:
    urlpatterns += [path("api/v2/", include("grades_api_v2.urls"))]

if "rest_framework" in settings.INSTALLED_APPS:
    from grades_api_v2.router import SharedAPIRootRouter

    def api_urls():
        return SharedAPIRootRouter.shared_router.urls

    urlpatterns += [path("api/v2/", include(api_urls()))]

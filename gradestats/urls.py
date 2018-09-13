from django.conf.urls import include, url
from django.contrib import admin
from grades.views import *
from grades_api.views import *
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.routers import SimpleRouter
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^index/$', index, name='index'),
    url(r'^course/$', index, name='index'),
    url(r'^course/(?P<course_code>[a-zA-Z\xc6\xd8\xc5\xf8\xe6\xe5]{1,8}[\d]{2,6})/$', course, name='course'),
    url(r'^course/(?P<course_code>[a-zA-Z\xc6\xd8\xc5\xf8\xe6\xe5]{1,8}[\d]{2,6})/tags/add/$', add_tag, name='add_tag'),
    url(r'^course/(?P<course_code>[a-zA-Z\xc6\xd8\xc5\xf8\xe6\xe5]{1,8}[\d]{2,6})/grades/$', get_grades, name='get_grades'),
    url(r'^search/$', search, name='search'),
    url(r'^about/$', about, name='about'),
    url(r'^report/$', report, name='report'),
    url(r'^api/$', api, name='api'),
    url(r'^admin/', include(admin.site.urls)),
]

router = SimpleRouter(trailing_slash=False)
router.register('api/courses', CourseViewSet)  # Create routes for Courses
regex = router.get_urls()[1].regex.pattern[1:-1]
router.register(regex + '/grades', GradeViewSet)  # Create routes for grades using regex from course route as base
router.register('api/index', CourseIndexViewSet)
router.register('api/typeahead/course', CourseTypeaheadViewSet)

urlpatterns += format_suffix_patterns(router.urls, allowed=['json'])
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

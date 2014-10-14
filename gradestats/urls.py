from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('grades.views',
    # Examples:
    url(r'^$', 'index', name='index'),
    url(r'^index/$', 'index', name='index'),
    url(r'^course/(?P<course_id>\d+)/$', 'course', name='course'),
    url(r'^course/(?P<course_id>\d+)/grades/$', 'get_grades', name='get_grades'),
    url(r'^search/$', 'search', name='search'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
)

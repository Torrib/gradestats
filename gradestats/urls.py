from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('grades.views',
    # Examples:
    url(r'^$', 'index', name='index'),
    url(r'^index/$', 'index', name='index'),
    url(r'^course/(?P<course_code>[a-zA-Z\xc5K]{2,5}[\d]{2,4})/$', 'course', name='course'),
    url(r'^course/(?P<course_code>[a-zA-Z\xc5K]{2,5}[\d]{2,4})/grades/$', 'get_grades', name='get_grades'),
    url(r'^search/$', 'search', name='search'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
)

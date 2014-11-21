from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('grades.views',
    url(r'^$', 'index', name='index'),
    url(r'^index/$', 'index', name='index'),
    url(r'^course/$', 'index', name='index'),
    url(r'^course/(?P<course_code>[a-zA-Z\xc6\xd8\xc5\xf8\xe6\xe5]{2,8}[\d]{2,4})/$', 'course', name='course'),
    url(r'^course/(?P<course_code>[a-zA-Z\xc6\xd8\xc5\xf8\xe6\xe5]{2,8}[\d]{2,4})/tags/add/$', 'add_tag', name='add_tag'),
    url(r'^course/(?P<course_code>[a-zA-Z\xc6\xd8\xc5\xf8\xe6\xe5]{2,8}[\d]{2,4})/grades/$', 'get_grades', name='get_grades'),
    url(r'^search/$', 'search', name='search'),
    url(r'^about/$', 'about', name='about'),
    url(r'^faq/$', 'faq', name='faq'),
    url(r'^report/$', 'report', name='report'),
    url(r'^api/$', 'api', name='api'),
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += patterns('grades_api.views',
    url(r'^api/courses/$', 'courses', name='courses'),
    url(r'^api/courses/(?P<course_code>[a-zA-Z\xc6\xd8\xc5\xf8\xe6\xe5]{2,8}[\d]{2,4})/$', 'course', name='api_course'),
    url(r'^api/courses/(?P<course_code>[a-zA-Z\xc6\xd8\xc5\xf8\xe6\xe5]{2,8}[\d]{2,4})/grades/$', 'grades',
        name='grades'),
    url(r'^api/courses/(?P<course_code>[a-zA-Z\xc6\xd8\xc5\xf8\xe6\xe5]{2,8}[\d]{2,4})/grades/'
        r'(?P<semester_code>[VHS]\d{4})/$', 'grade', name='grade')
)

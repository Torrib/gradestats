from django.contrib import admin

from grades.models import *

class CourseAdmin(admin.ModelAdmin):
    model = Course
    
class GradeAdmin(admin.ModelAdmin):
    model = Grade


admin.site.register(Course, CourseAdmin)
admin.site.register(Grade, GradeAdmin)

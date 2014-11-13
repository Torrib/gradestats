from django.contrib import admin

from grades.models import *


class CourseAdmin(admin.ModelAdmin):
    model = Course


class GradeAdmin(admin.ModelAdmin):
    list_display = ('course', 'semester_code', 'average_grade')
    model = Grade


class TagAdmin(admin.ModelAdmin):
    list_display = ('tag', 'course_list')
    model = Tag

    def course_list(self, obj):
        return ", ".join([c.code for c in obj.courses.all()])

admin.site.register(Course, CourseAdmin)
admin.site.register(Grade, GradeAdmin)
admin.site.register(Tag, TagAdmin)

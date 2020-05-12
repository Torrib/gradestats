from django.contrib import admin

from grades.models import *


class CourseAdmin(admin.ModelAdmin):
    list_display = ("code", "place", "has_had_digital_exam", "exam_type", "grade_type")
    list_filter = ("place", "has_had_digital_exam", "exam_type", "grade_type")
    search_fields = ["code"]
    model = Course


class GradeAdmin(admin.ModelAdmin):
    search_fields = ["course__code"]
    list_filter = ("semester_code", "digital_exam")
    list_display = ("course", "semester_code", "average_grade")
    model = Grade


class TagAdmin(admin.ModelAdmin):
    list_display = ("tag", "course_list")
    model = Tag

    def course_list(self, obj):
        return ", ".join([c.code for c in obj.courses.all()])


admin.site.register(Course, CourseAdmin)
admin.site.register(Grade, GradeAdmin)
admin.site.register(Tag, TagAdmin)

from django.contrib import admin

from grades.models import *


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("code", "place", "has_had_digital_exam", "exam_type", "grade_type")
    list_filter = ("place", "has_had_digital_exam", "exam_type", "grade_type")
    search_fields = ["code"]
    model = Course


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    search_fields = ["course__code"]
    list_filter = ("semester", "year", "digital_exam")
    list_display = ("course", "semester", "year", "average_grade")
    model = Grade


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("tag", "course_list")
    model = Tag

    def course_list(self, obj):
        return ", ".join([c.code for c in obj.courses.all()])


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    search_fields = ["course__code"]
    list_display = ("course", "contact_email", "created_date")
    model = Report

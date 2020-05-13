from rest_framework import serializers

from grades.models import Grade, Course, Tag, Report


class CourseSerializer(serializers.ModelSerializer):
    course_level = serializers.CharField()
    attendee_count = serializers.IntegerField()

    class Meta:
        model = Course
        fields = (
            "id",
            "norwegian_name",
            "short_name",
            "code",
            "faculty_code",
            "exam_type",
            "grade_type",
            "place",
            "has_had_digital_exam",
            "english_name",
            "credit",
            "study_level",
            "taught_in_spring",
            "taught_in_autumn",
            "taught_from",
            "taught_in_english",
            "last_year_taught",
            "content",
            "learning_form",
            "learning_goal",
            "course_level",
            "average",
            "watson_rank",
            "attendee_count",
        )


class GradeSerializer(serializers.ModelSerializer):
    attendee_count = serializers.IntegerField()

    class Meta:
        model = Grade
        fields = (
            "id",
            "course",
            "semester_code",
            "average_grade",
            "digital_exam",
            "passed",
            "a",
            "b",
            "c",
            "d",
            "e",
            "f",
            "attendee_count",
        )


class TagSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="tag")

    class Meta:
        model = Tag
        fields = (
            "id",
            "name",
        )


class ReportSerializer(serializers.ModelSerializer):
    course = serializers.SlugRelatedField(
        queryset=Course.objects.all(), allow_null=True, slug_field="code",
    )

    class Meta:
        model = Report
        fields = ("id", "created_date", "description", "course", "contact_email")
        read_only_fields = ("created_date",)

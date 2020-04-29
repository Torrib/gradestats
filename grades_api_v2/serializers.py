from rest_framework import serializers

from grades.models import Grade, Course, Tag


class CourseSerializer(serializers.ModelSerializer):
    course_level = serializers.CharField()

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
            "have_had_digital_exam",
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

from django.contrib.auth.models import User
from rest_framework import serializers

from grades.models import (
    Grade,
    Course,
    Tag,
    Report,
    CourseTag,
    Faculty,
    Department,
    Semester,
    Favourite,
)


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
            "department",
        )


class GradeSerializer(serializers.ModelSerializer):
    attendee_count = serializers.IntegerField()
    semester_display = serializers.CharField(source="get_semester_display")
    semester_code = serializers.CharField()

    class Meta:
        model = Grade
        fields = (
            "id",
            "course",
            "semester",
            "semester_display",
            "year",
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


class CourseTagSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="tag.tag")
    course = serializers.SlugRelatedField(
        queryset=Course.objects.all(), slug_field="code",
    )
    user = serializers.SerializerMethodField()

    def get_user(self, obj: CourseTag):
        request = self.context.get("request")
        user: User = request.user
        if user.is_staff:
            return obj.created_by_id
        return None

    def create(self, validated_data):
        """
        Handle tag creation manually because a tag by the given name may already exist.
        """
        name = validated_data.pop("tag").pop("tag")
        tag, created = Tag.objects.get_or_create(tag=name)
        validated_data.update(tag=tag)
        return super().create(validated_data)

    class Meta:
        model = CourseTag
        fields = ("id", "name", "course", "user")


class TagSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="tag")
    courses = serializers.SlugRelatedField(
        queryset=Course.objects.all(), slug_field="code", many=True
    )

    class Meta:
        model = Tag
        fields = (
            "id",
            "name",
            "courses",
        )


class FavouriteSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        queryset=User.objects.all(), slug_field="username"
    )
    course = serializers.SlugRelatedField(
        queryset=Course.objects.all(), slug_field="code"
    )

    class Meta:
        model = Favourite
        fields = (
            "id",
            "user",
            "course",
            "created_date",
        )


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    def get_full_name(self, obj: User):
        return obj.get_full_name()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "full_name",
            "first_name",
            "last_name",
            "is_superuser",
            "is_staff",
            "is_active",
            "date_joined",
            "last_login",
        )


class ReportSerializer(serializers.ModelSerializer):
    course = serializers.SlugRelatedField(
        queryset=Course.objects.all(), allow_null=True, slug_field="code",
    )

    class Meta:
        model = Report
        fields = ("id", "created_date", "description", "course", "contact_email")
        read_only_fields = ("created_date",)


class FacultySerializer(serializers.ModelSerializer):
    class Meta:
        model = Faculty
        fields = "__all__"


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = "__all__"


class TIAObjectListRefreshSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    limit = serializers.IntegerField(default=100)
    skip = serializers.IntegerField(default=0)

    class Meta:
        fields = (
            "username",
            "password",
            "limit",
            "skip",
        )


class KarstatGradeReportSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    department = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all())
    year = serializers.IntegerField()
    semester = serializers.ChoiceField(choices=Semester.choices)

    class Meta:
        fields = (
            "username",
            "password",
            "department",
            "year",
            "semester",
        )


class NSDGradeReportSerializer(serializers.Serializer):
    course = serializers.SlugRelatedField(
        queryset=Course.objects.all(), slug_field="code",
    )
    year = serializers.IntegerField()
    semester = serializers.ChoiceField(choices=Semester.choices)

    class Meta:
        fields = (
            "course",
            "year",
            "semester",
        )

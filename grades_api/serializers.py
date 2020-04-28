from rest_framework import serializers
from grades.models import *


class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = ('semester_code', 'average_grade', 'digital_exam', 'passed', 'a', 'b', 'c', 'd', 'e', 'f')


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ('norwegian_name', 'short_name', 'code', 'faculty_code', 'english_name', 'credit', 'study_level',
                  'taught_in_spring', 'taught_in_autumn', 'taught_from', 'taught_in_english', 'last_year_taught',
                  'content', 'learning_form', 'learning_goal', 'exam_type', 'grade_type', 'place', 'have_had_digital_exam')


class CourseIndexSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ('code', 'norwegian_name', 'faculty_code')


class CourseTypeaheadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ('code', 'norwegian_name', 'english_name')
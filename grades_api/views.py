from rest_framework import viewsets
from grades_api.serializers import *
from django.shortcuts import get_object_or_404
from rest_framework.response import Response


class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    lookup_field = 'code'

    def retrieve(self, request, *args, **kwargs):
        queryset = Course.objects.all()
        course = get_object_or_404(queryset, code=kwargs['code'].upper())
        serializer = CourseSerializer(course)
        return Response(serializer.data)


class GradeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    lookup_field = 'semester_code'

    def retrieve(self, request, *args, **kwargs):
        course = get_object_or_404(Course, code=kwargs['code'].upper())
        grade = get_object_or_404(course.grade_set, semester_code=kwargs['semester_code'].upper())
        serializer = GradeSerializer(grade)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        course = get_object_or_404(Course, code=kwargs['code'].upper())
        grades = course.grade_set.all()
        serializer = GradeSerializer(grades, many=True)
        return Response(serializer.data)

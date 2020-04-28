from rest_framework import viewsets
from grades_api.serializers import *
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from django.db.models import Q


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
        course = get_object_or_404(Course, code=kwargs['course_code'].upper())
        grade = get_object_or_404(course.grade_set, semester_code=kwargs['semester_code'].upper())
        serializer = GradeSerializer(grade)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        course = get_object_or_404(Course, code=kwargs['course_code'].upper())
        grades = course.grade_set.all()
        serializer = GradeSerializer(grades, many=True)
        return Response(serializer.data)


class CourseIndexViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseIndexSerializer


class CourseTypeaheadViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseTypeaheadSerializer
    lookup_field = 'code'

    def list(self, request, *args, **kwargs):
        if 'query' not in request.GET:
            return Response("")

        if 'query' in request.GET:
            query = request.GET.get('query')
        else:
            query = ""

        self.queryset = self.queryset.filter(Q(code__istartswith=query) |
                                             Q(norwegian_name__istartswith=query) |
                                             Q(english_name__istartswith=query))

        tag = Tag.objects.filter(Q(tag__istartswith=query))

        self.queryset = list(self.queryset)

        if tag:
            self.queryset.extend(c for c in tag[0].courses.all() if c not in self.queryset)

        serializer = CourseTypeaheadSerializer(self.queryset, many=True)
        return Response(serializer.data)

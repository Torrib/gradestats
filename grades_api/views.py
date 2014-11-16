from django.shortcuts import HttpResponse, get_object_or_404, render
from django.http import HttpResponseNotFound
from rest_framework.renderers import JSONRenderer
from serializers import *


class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


def index(request):
    return render(request, 'api_index.html')


def courses(request):
    courses = Course.objects.all()
    serializer = CourseSerializer(courses, many=True)

    return JSONResponse({'courses': serializer.data}, status=200)


def course(request, course_code):
    course = get_object_or_404(Course, code=course_code.upper())
    serializer = CourseSerializer(course, many=False)

    return JSONResponse({'course': serializer.data}, status=200)


def grades(request, course_code):
    course = get_object_or_404(Course, code=course_code.upper())
    course_grades = course.grade_set.all()
    serializer = GradeSerializer(course_grades, many=True)

    return JSONResponse({'grades': serializer.data}, status=200)


def grade(request, course_code, semester_code):
    course = get_object_or_404(Course, code=course_code.upper())
    course_grades = course.grade_set.filter(semester_code=semester_code)

    if len(course_grades) == 1:
        serializer = GradeSerializer(course_grades[0], many=False)
        return JSONResponse({'grades': serializer.data}, status=200)
    else:
        return HttpResponseNotFound("{grades: {}}")
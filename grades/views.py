from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.core import serializers
from django.db.models import Q

from grades.models import Course, Grade


def index(request):
    courses = Course.objects.all()
    return render(request, 'index.html', {'courses': courses})


def course(request, course_code):
    course = get_object_or_404(Course, code=course_code)
    return render(request, 'course.html', {'course': course})


def get_grades(request, course_code):
    course = get_object_or_404(Course, code=course_code)
    grades = course.grade_set.all()
    json = serializers.serialize('json', grades)
    return HttpResponse(json) 


def search(request):
    if 'query' in request.GET and request.GET['query']:
        query = request.GET['query']
        courses = Course.objects.filter(Q(norwegian_name__icontains=query) | Q(english_name__icontains=query) |
                                        Q(short_name__icontains=query) | Q(code__icontains=query))
        return render(request, 'index.html', {'courses': courses, 'query': query})
    else:
        return render(request, 'search.html') 
    

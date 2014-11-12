from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.core import serializers
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from grades.models import Course, Grade


def index(request):
    courses = Course.objects.all()
    paginator = Paginator(courses, 20)
    page = request.GET.get('page')

    try:
        courses = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        courses = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        courses = paginator.page(paginator.num_pages)

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

        paginator = Paginator(courses, 20)
        page = request.GET.get('page')

        try:
            courses = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            courses = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            courses = paginator.page(paginator.num_pages)

        return render(request, 'index.html', {'courses': courses, 'query': query})
    else:
        return render(request, 'search.html')


def report(request):
    if 'course' in request.GET and request.GET['course']:
        return render(request, 'report.html', {'sent': True})
    else:
        return render(request, 'report.html')



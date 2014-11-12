# -*- coding: utf-8 -*-
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.core import serializers
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from grades.models import Course, Grade, Tag
from itertools import chain


def index(request):
    if 'faculty_code' in request.GET and request.GET['faculty_code']:
        courses = Course.objects.filter(faculty_code=int(request.GET['faculty_code']))
    else:
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
    tags = list(Tag.objects.filter(course=course))

    return render(request, 'course.html', {'course': course, 'tags': tags})


def get_grades(request, course_code):
    course = get_object_or_404(Course, code=course_code)
    grades = course.grade_set.all()
    json = serializers.serialize('json', grades)
    return HttpResponse(json) 


def faculty_filter(request, faculty_code):
    courses = Course.objects.filter(faculty_code=faculty_code)
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


def search(request):
    if 'query' in request.GET and request.GET['query']:
        query = request.GET['query']

        courses = list(Course.objects.filter(Q(norwegian_name__icontains=query) | Q(english_name__icontains=query) |
                                             Q(short_name__icontains=query) | Q(code__icontains=query)))

        tags = Tag.objects.filter(Q(tag__icontains=query))

        for tag in tags:
            if tag.course not in courses:
                courses.append(tag.course)

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
    if 'course' in request.POST and request.POST['course']:
        messages = []
        message = {}
        message['tags'] = 'success'
        message['message'] = u"Takk for at du hjelper til med å gjøre denne siden bedre!"
        messages.append(message)
        return render(request, 'report.html', {'messages': messages})
    else:
        return render(request, 'report.html')



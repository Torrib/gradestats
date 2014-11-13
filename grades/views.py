# -*- coding: utf-8 -*-
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.core import serializers
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from grades.models import Course, Grade, Tag
from grades.forms import *


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
    tags = list(Tag.objects.filter(courses=course))

    return render(request, 'course.html', {'course': course, 'tags': tags})


def add_tag(request, course_code):
    course = get_object_or_404(Course, code=course_code)
    form = AddTagForm(request.POST)

    if form.is_valid():
        tag = Tag.objects.get_or_create(tag=form.cleaned_data['tag'])
        if tag[1]:
            print "Created new tag %s" % tag[0].tag
        tag[0].save()
        tag[0].courses.add(course)

    return redirect('course', course_code=course_code)


def get_grades(request, course_code):
    course = get_object_or_404(Course, code=course_code)
    grades = course.grade_set.all()
    json = serializers.serialize('json', grades)
    return HttpResponse(json)


def search(request):
    form = SearchForm(request.GET)
    if form.is_valid():
        query = form.cleaned_data['query']
        courses = list(Course.objects.filter(Q(norwegian_name__icontains=query) | Q(english_name__icontains=query) |
                                             Q(short_name__icontains=query) | Q(code__icontains=query)))
        tags = list(Tag.objects.filter(Q(tag__icontains=query)))

        for tag in tags:
            courses.extend(c for c in tag.courses.all() if c not in courses)

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
    form = ReportErrorForm(request.POST)

    if form.is_valid():
        messages = [{'tags': 'success', 'text': u"Takk for at du hjelper til med å gjøre denne siden bedre!"}]
        return render(request, 'report.html', {'messages': messages})
    else:
        return render(request, 'report.html')



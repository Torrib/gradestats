# -*- coding: utf-8 -*-
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from grades.models import *
from grades.forms import *
from django.core.files import File
import os
import uuid


def navbar_render(request, args, dictionary={}):

    kwargs = {
        'navbar': NavbarItems.get_items()
    }
    kwargs.update(dictionary)

    return render(request, args, kwargs)


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

    return navbar_render(request, 'index.html', {'courses': courses, 'faculties': Faculties.get_faculties()})


def course(request, course_code):
    course = get_object_or_404(Course, code=course_code.upper())
    tags = list(Tag.objects.filter(courses=course))

    return navbar_render(request, 'course.html', {'course': course, 'tags': tags})


def add_tag(request, course_code):
    course = get_object_or_404(Course, code=course_code.upper())
    form = AddTagForm(request.POST)

    if form.is_valid():
        tag = Tag.objects.get_or_create(tag=form.cleaned_data['tag'].lower())
        tag = tag[0]
        tag.save()
        tag.courses.add(course)

    return redirect('course', course_code=course_code.upper())


def get_grades(request, course_code):
    url = "/api/courses/%s/grades" % course_code

    return redirect(url)


def search(request):
    form = SearchForm(request.GET)
    query = form.data['query']
    faculty_code = form.data['faculty_code']

    if len(query) == 0:
        courses = Course.objects.all()
    else:
        courses = Course.objects.filter(Q(norwegian_name__icontains=query) | Q(english_name__icontains=query) |
                                        Q(short_name__icontains=query) | Q(code__icontains=query))
    if faculty_code != "-1":
        courses = courses.filter(faculty_code=faculty_code)

    tag = Tag.objects.filter(tag=query.lower())

    courses = list(courses)

    if tag:
        courses.extend(c for c in tag[0].courses.all() if c not in courses)

    paginator = Paginator(courses, 20)
    page = request.GET.get('page')

    try:
        courses = paginator.page(page)
    except PageNotAnInteger:
        courses = paginator.page(1)
    except EmptyPage:
        courses = paginator.page(paginator.num_pages)

    return navbar_render(request, 'index.html', {'courses': courses, 'query': query, 'selected': str(faculty_code),
                                  'faculties': Faculties.get_faculties()})


def report(request):
    form = ReportErrorForm(request.POST)

    if form.is_valid():
        messages = [{'tags': 'success', 'text': u"Takk for at du hjelper til med å gjøre denne siden bedre!"}]

        file_path = 'reports/' + str(uuid.uuid4()) + '.xml'
        while os.path.isfile(file_path):
            file_path = 'reports/' + str(uuid.uuid4()) + '.xml'

        f = open(file_path, 'w+')
        xml_file = File(f)

        text = (
            u"<?xml version=\"1.0\" encoding=\"UTF-8\"?>",
            u"<!DOCTYPE bank SYSTEM \"report.dtd\">",
            u"<report xmlns=\"http://www.w3schools.com\"",
            u"\txmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\"",
            u"\txsi:schemaLocation=\"report.xsd\">",
            u"\t<course>", u"\t\t" + form.cleaned_data['course_code'], u"\t</course>",
            u"\t<semester>", u"\t\t" + form.cleaned_data['semester_code'], u"\t</semester>",
            u"\t<description>", u"\t\t" + form.cleaned_data['description'], u"\t</description>",
            u"</report>"
        )

        xml_file.write(u'\n'.join(text).encode('utf8'))
        xml_file.close()

        return navbar_render(request, 'report.html', {'messages': messages})
    else:
        return navbar_render(request, 'report.html')


def about(request):
    return navbar_render(request, 'about.html')


def faq(request):
    return navbar_render(request, 'faq.html')

# -*- coding: utf-8 -*-
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gradestats.settings")
django.setup()

from bs4 import BeautifulSoup
import glob
from grades.models import Grade, Course
import json
import requests


def create_course(code):
    base_url = "http://www.ime.ntnu.no/api/course/"
    resp = requests.get(url=base_url + code)
    data = json.loads(resp.text)

    if not data["course"]:
        return None

    course = Course()
    course.code = "IT2901"
    course.norwegian_name = data["course"]["norwegianName"]
    course.english_name = data["course"]["englishName"]
    course.code = data["course"]["code"]
    course.credit = data["course"]["credit"]
    course.study_level = data["course"]["studyLevelCode"]
    course.last_year_taught = data["course"]["lastYearTaught"]
    course.taught_from = data["course"]["taughtFromYear"]
    course.taught_in_autumn = data["course"]["taughtInAutumn"]
    course.taught_in_spring = data["course"]["taughtInSpring"]
    course.taught_in_english = data["course"]["taughtInEnglish"]

    for info in data['course']['infoType']:
        if info['code'] == "INNHOLD" and 'text' in info:
            course.content = info['text']
        if info['code'] == u"LÆRFORM" and 'text' in info:
            course.learning_form = info['text']
        if info['code'] == u"MÅL" and 'text' in info:
            course.learning_goal = info['text']

    return course

files = glob.glob('grades_data/*.html')
for f in files:
    reader = open(f, 'r')
    html = reader.read()
    soup = BeautifulSoup(html, 'html5')
    tables = soup.find_all('table')

    # Semester info
    table_info = tables[len(tables) - 4]
    rows_info = table_info.find_all('tr')
    td_info = rows_info[1].find_all('td')
    temp = td_info[1].string.split('-')
    semester_code = '%s%s' % (temp[0].strip(), temp[1].strip()[0])
    print "processing %s" % semester_code

    # Grade info
    rows_grades = soup.find_all(class_="tableRow")
    # row 5 and down is subjects
    for i in range(0, len(rows_grades) - 1):
        td_grades = rows_grades[i].find_all('td')
        subject_code = td_grades[0].string.split('-')
        subject_code = subject_code[0].strip()
        subjects = Course.objects.filter(code=subject_code)
        if not subjects:
            if "AVH" in subject_code:
                continue
            course = create_course(subject_code)
            if not course:
                continue
            course.save()
        else:
            course = subjects[0]

        grades = Grade.objects.filter(course=course, semester_code=semester_code)
        if not grades:
            grades = Grade()
            grades.course = course
            grades.semester_code = semester_code
            grades.f = int(td_grades[6].string.strip())
            grades.a = int(td_grades[13].string.strip())
            grades.b = int(td_grades[14].string.strip())
            grades.c = int(td_grades[15].string.strip())
            grades.d = int(td_grades[16].string.strip())
            grades.e = int(td_grades[17].string.strip())

            if((grades.a + grades.b + grades.c + grades.d + grades.e) == 0):
                grades.average_grade = 0;
            else:
                grades.average_grade = ((grades.a * 5) + (grades.b * 4) + (grades.c * 3) + (grades.d * 2) + (grades.e * 1))/(grades.a + grades.b + grades.c + grades.d + grades.e)

            grades.save()
            print "%s - %s added" % (course, semester_code)

# -*- coding: utf-8 -*-
import os
import django
from bs4 import BeautifulSoup
import json
import requests
import sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gradestats.settings")
django.setup()
from grades.models import Grade, Course


def login(username, password):
    session = requests.session()
    login_data = dict(feidename=username, password=password, org="ntnu.no", asLen="255")
    page = session.get("https://innsida.ntnu.no/sso/?target=KarstatProd")

    login_url = "https://idp.feide.no/simplesaml/module.php/feide/login.php"

    soup = BeautifulSoup(page.text)

    form = soup.findAll("form", {"name": "f"})[0]

    login_data["AuthState"] = form.findAll("input", {"name": "AuthState"})[0]["value"]
    login_url += form["action"]

    reply = session.post(login_url, data=login_data)
    reply_soup = BeautifulSoup(reply.text)

    sso_wrapper_data = dict()
    sso_wrapper_data["SAMLResponse"] = reply_soup.findAll("input", {"name": "SAMLResponse"})[0]["value"]
    sso_wrapper_data["RelayState"] = reply_soup.findAll("input", {"name": "RelayState"})[0]["value"]

    sso_wrapper_url = reply_soup.findAll("form")[0]["action"]

    karstat = session.post(sso_wrapper_url, data=sso_wrapper_data)

    karstat_soup = BeautifulSoup(karstat.text)

    karstat_url = "http://www.ntnu.no" + karstat_soup.findAll("form", {"name": "menuform"})[0]["action"]

    session.post(karstat_url, data={"reportType": "2"})

    return session


def create_course(code):
    base_url = "http://www.ime.ntnu.no/api/course/"
    resp = requests.get(url=base_url + code)
    if not resp:
        return None
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

    course.save()
    return course


def parse_data(data):
    soup = BeautifulSoup(data, 'html5')
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

            s = grades.a + grades.b + grades.c + grades.d + grades.e
            if s == 0:
                grades.average_grade = 0
            else:
                grades.average_grade = (grades.a * 5) + (grades.b * 4) + (grades.c * 3) + (grades.d * 2) + grades.e / s

            grades.save()
            print "%s - %s added" % (course.english_name, semester_code)


def main():
    if len(sys.argv) < 3:
        print "Usage: grades.py username password"
        exit(1)

    karstat_url = "http://www.ntnu.no/karstat/fs582001Action.do"
    username = sys.argv[1]
    password = sys.argv[2]
    session = login(username, password)
    karstat_data = dict()
    karstat_data["yearExam"] = "2013"
    karstat_data["semesterExam"] = "HØST"
    karstat_data["numberOfYears"] = "0"
    karstat_data["minCandidates"] = "3"
    karstat_data["yearExam"] = "2013"

    # Iterate over years
    for y in range(2014, 2010):
        print "Getting data for " + repr(y)
        karstat_data["yearExam"] = "" + repr(y)
        # Iterate over faculties
        for i in range(61, 68):
            faculty_url = "http://www.ntnu.no/karstat/menuAction.do?faculty=" + repr(i)
            print "Getting data for faculty " + repr(i)
            session.get(faculty_url)
            # Get data for autumn
            karstat_data["semesterExam"] = "HØST"
            grades_data = session.post(karstat_url, data=karstat_data)
            parse_data(grades_data.text)
            # Get data for spring
            karstat_data["semesterExam"] = "VÅR"
            grades_data = session.post(karstat_url, data=karstat_data)
            parse_data(grades_data.text)
main()
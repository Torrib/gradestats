# -*- coding: utf-8 -*-
import os
import django
from bs4 import BeautifulSoup
import json
import requests
import getpass

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


def create_course(code, faculty):
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

    if 'infoType' in data['course']:
        for info in data['course']['infoType']:
            if info['code'] == "INNHOLD" and 'text' in info:
                course.content = info['text']
            if info['code'] == u"LÆRFORM" and 'text' in info:
                course.learning_form = info['text']
            if info['code'] == u"MÅL" and 'text' in info:
                course.learning_goal = info['text']
    course.faculty_code = faculty
    course.save()
    return course


def parse_data(data, exam, faculty):
    soup = BeautifulSoup(data, 'html5')
    tables = soup.find_all('table')

    # Semester info
    table_info = tables[len(tables) - 4]
    rows_info = table_info.find_all('tr')
    td_info = rows_info[1].find_all('td')
    temp = td_info[1].string.split('-')
    semester_code = ""

    if exam == "VÅR":
        semester_code = "V"
    elif exam == "SOM":
        semester_code = "S"
    elif exam == "HØST":
        semester_code = "H"

    semester_code += '%s' % (temp[0].strip())

    # Grade info
    rows_grades = soup.find_all(class_="tableRow")
    # row 5 and down is subjects
    print("found %d exams from %s" % (len(rows_grades) - 1, semester_code))
    for i in range(0, len(rows_grades) - 1):
        td_grades = rows_grades[i].find_all('td')
        subject_code = td_grades[0].string.split('-')
        subject_code = subject_code[0].strip()
        subjects = Course.objects.filter(code=subject_code)
        if not subjects:
            if "AVH" in subject_code:
                continue
            course = create_course(subject_code, faculty)
            if not course:
                continue
        else:
            course = subjects[0]

        grades = Grade.objects.filter(course=course, semester_code=semester_code)
        if not grades:
            grades = Grade()
            attending = int(td_grades[5].string.strip())

            grades.course = course
            grades.semester_code = semester_code
            grades.f = int(td_grades[6].string.strip())

            passing = attending - grades.f

            grades.a = round((int(td_grades[13].string.strip()) / 100.0) * passing)
            grades.b = round((int(td_grades[14].string.strip()) / 100.0) * passing)
            grades.c = round((int(td_grades[15].string.strip()) / 100.0) * passing)
            grades.d = round((int(td_grades[16].string.strip()) / 100.0) * passing)
            grades.e = round((int(td_grades[17].string.strip()) / 100.0) * passing)

            s = grades.a + grades.b + grades.c + grades.d + grades.e + grades.f

            if s - grades.f == 0:
                grades.passed = passing

            if s == 0:
                grades.average_grade = 0
            else:
                grades.average_grade = (grades.a * 5.0 + grades.b * 4 + grades.c * 3 + grades.d * 2 + grades.e) / s

            grades.save()


def main():

    karstat_url = "http://www.ntnu.no/karstat/fs582001Action.do"
    username = input("Username: ")
    password = getpass.getpass()
    from_year = input("From year: ")
    to_year = input("To year: ")
    from_faculty = input("From faculty: ")
    to_faculty = input("To faculty: ")

    session = login(username, password)
    karstat_data = dict()
    karstat_data["yearExam"] = "2013"
    karstat_data["semesterExam"] = "HØST"
    karstat_data["numberOfYears"] = "0"
    karstat_data["minCandidates"] = "3"
    karstat_data["yearExam"] = "2013"

    exams = ["VÅR", "SOM", "HØST"]

    # Set default values
    if len(username) == 0:
        print("Username required")
        exit(1)
    if len(password) == 0:
        print("Password required")
        exit(1)
    if len(from_year) == 0:
        from_year = 2014
    if len(to_year) == 0:
        to_year = 2015
    if len(from_faculty) == 0:
        from_faculty = 63
    if len(to_faculty) == 0:
        to_faculty = 64

    # Iterate over years
    for y in range(int(from_year), int(to_year)):
        print("Getting data for " + repr(y))
        karstat_data["yearExam"] = "" + repr(y)
        # Iterate over faculties
        for i in range(int(from_faculty), int(to_faculty)):
            faculty_url = "http://www.ntnu.no/karstat/menuAction.do?faculty=" + repr(i)
            print("Getting data for faculty " + repr(i))
            session.get(faculty_url)
            for exam in exams:
                karstat_data["semesterExam"] = exam
                grades_data = session.post(karstat_url, data=karstat_data)
                parse_data(grades_data.text, exam, i)
main()
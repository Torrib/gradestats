import os
import json
import getpass
import django
import json
import re
from bs4 import BeautifulSoup
import requests
headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0' }


def getCourseData(code, faculty):
    tia_url = "https://api.ntnu.no/rest/v4/emne/emnekode/194_"
    base_url_no = "https://www.ntnu.no/studier/emner/" + code
    data_no = requests.get(url=base_url_no, headers=headers)
    soup_no = BeautifulSoup(data_no.text, 'html5lib')
    #tia = requests.get(url=tia_url + code + "_1").text
    course_detail_h1 = "Ingen info for gitt studieår"
    try:
        course_detail_h1 = soup_no.find_all('div', {'id': 'course-details'})[0].h1.get_text().strip()
    except IndexError:
        print("Something very wrong for course: " + code)
    if (course_detail_h1 != "Ingen info for gitt studieår"):
        base_url_eng = "https://www.ntnu.edu/studies/courses/" + code
        data_eng = requests.get(url=base_url_eng, headers=headers)
        soup_eng = BeautifulSoup(data_eng.text, 'html5lib')
        facts_about_course = ""
        try:
            facts_about_course = soup_no.findAll('div', {'class': 'card-body'})[1].p.get_text().split(":")
        except IndexError:
            print("Cannot find facts about course at all, code " + code)
        credit = -1
        try:
            credit = float(facts_about_course[2].split("\n")[2][20:24])
        except ValueError:
            print("Not valid number, number is: ", facts_about_course[2].split("\n")[2])
        norwegianNameRaw = soup_no.title.get_text().split("-")
        norwegianName = ""
        if (len(norwegianNameRaw) > 4):
            norwegianName = norwegianNameRaw[1][1:len(norwegianNameRaw[1])]
            for i in range(2, len(norwegianNameRaw) - 4):
                norwegianName += "-"
                norwegianName += norwegianNameRaw[i]
            norwegianName += "-"
            norwegianName += norwegianNameRaw[len(norwegianNameRaw) - 3][0:len(norwegianNameRaw[len(norwegianNameRaw) - 3]) - 1]
        else:
            norwegianName = norwegianNameRaw[1][1:len(norwegianNameRaw[1]) - 1]
        englishNameRaw = soup_eng.title.get_text().split("-")
        englishName = ""
        if (len(englishNameRaw) > 4):
            englishName = englishNameRaw[1][1:len(englishNameRaw[1])]
            for i in range(2, len(englishNameRaw) - 4):
                englishName += "-"
                englishName += englishNameRaw[i]
            englishName += "-"
            englishName += englishNameRaw[len(englishNameRaw) - 3][0:len(englishNameRaw[len(englishNameRaw) - 3]) - 1]
        else:
            englishName = englishNameRaw[1][1:len(englishNameRaw[1]) - 1]
        courseLevelText = facts_about_course[3].split("\n")[0][1:len(facts_about_course[3].split("\n")[0])]
        study_level = courseLevel(courseLevelText, code)
        last_year_taught = 0
        taught_from = 2008
        taught_in_autumn = False
        taught_in_spring = False
        taught_in_english = False
        undervisning = soup_no.findAll('div', {'class': 'card-body'})[2]
        classes = undervisning.get_text().split("Undervises")
        place = ""
        try:
            place = undervisning.get_text().split("Sted:")[1].strip()
        except IndexError:
            print("Cannot get place")
        for elements in classes:
            if("HØST" in elements):
                taught_in_autumn = True
            if("VÅR" in elements):
                taught_in_spring = True
            if("Engelsk" in elements):
                taught_in_english = True
        content = None
        infoType = []
        exam_type = ""
        grade_type = ""
        try:
            exam_typeRaw = soup_no.find_all('div', {'class': 'content-assessment'})[0].p.contents[0].strip().split(":")[1]
            exam_type = exam_typeRaw[1:len(exam_typeRaw)]
        except IndexError:
            print("Cannot get exam type")
        try:
            grade_typeRaw = soup_no.find_all('div', {'class': 'content-assessment'})[0].p.contents[2].strip().split(":")[1]
            grade_type = grade_typeRaw[1:len(grade_typeRaw)]
        except IndexError:
            print("Cannot get exam type")
        try:
            content = soup_no.find_all('div', {'id': 'course-content-toggler'})[0].p.get_text()
            infoType.append({"code": "INNHOLD", "text": content})
        except IndexError:
            print("Cannot get content")
        learning_form = None
        try:
            learning_form = soup_no.find_all('div', {'id': 'learning-method-toggler'})[0].p.get_text()
            infoType.append({"code": "LÆRFORM", "text": learning_form})
        except IndexError:
            print("Cannot get learning from")
        learning_goal = None
        try:
            learning_goal = soup_no.find_all('div', {'id': 'learning-goal-toggler'})[0].p.get_text()
            infoType.append({"code": "MÅL", "text": learning_goal})
        except IndexError:
            print("Cannot get learning goal")

        course = {
            "course": {
                "norwegianName": norwegianName,
                "englishName": englishName,
                "code": code,
                "credit": credit,
                "studyLevelCode": study_level,
                "lastYearTaught": last_year_taught,
                "taughtFromYear": taught_from,
                "taughtInAutumn": taught_in_autumn,
                "taughtInSpring": taught_in_spring,
                "taughtInEnglish": taught_in_english,
                "infoType": infoType,
                "examType": exam_type,
                "gradeType": grade_type,
                "place": place
            }
        }
        return json.dumps(course)

    else:
        print("Grades.no - API - Fallback for course: " + code)
        base_url = "https://grades.no/api/courses/"
        resp = requests.get(url=base_url + code, headers=headers)
        data = json.loads(resp.text) if resp.status_code == 200 else None
        if (data and not "detail" in data):
            infoType = []
            if "content" in data:
                infoType.append({"code": "INNHOLD", "text": data["content"]})
            if "learning_form" in data:
                infoType.append(
                    {"code": "LÆRFORM", "text": data["learning_form"]})
            if "learning_goal" in data:
                infoType.append({"code": "MÅL", "text": data["learning_goal"]})
            course = {
                "course": {
                    "norwegianName": data["norwegian_name"],
                    "englishName": data["english_name"],
                    "code": code,
                    "credit": data["credit"],
                    "studyLevelCode": data["study_level"],
                    "lastYearTaught": data["last_year_taught"],
                    "taughtFromYear": data["taught_from"],
                    "taughtInAutumn": data["taught_in_autumn"],
                    "taughtInSpring": data["taught_in_spring"],
                    "taughtInEnglish": data["taught_in_english"],
                    "infoType": infoType,
                    "examType": "",
                    "gradeType": "",
                    "place": ""
                }
            }
            return json.dumps(course)

        print("No information about course: " + code +  " could be found - skipping")
        return None


def courseLevel(courseLevelText, code):
    if(courseLevelText == "Doktorgrads nivå"):
        return 900
    elif (courseLevelText == "Videreutdanning lavere grad"):
        return 800
    elif (courseLevelText == "Høyere grads nivå"):
        return 500
    elif (courseLevelText == "Fjerdeårsemner, nivå IV"):
        return 400
    elif (courseLevelText == "Tredjeårsemner, nivå III"):
        return 300
    elif (courseLevelText == "Videregående emner, nivå II"):
        return 200
    elif (courseLevelText == "Grunnleggende emner, nivå I"):
        return 100
    elif (courseLevelText == "Lavere grad, redskapskurs"):
        return 90
    elif (courseLevelText == "Norsk for internasjonale studenter"):
        return 80
    elif (courseLevelText == "Examen facultatum"):
        return 71
    elif (courseLevelText == "Examen philosophicum"):
        return 70
    elif (courseLevelText == "Forprøve/forkurs"):
        return 60
    else:
        print(courseLevelText, code)
        return -1
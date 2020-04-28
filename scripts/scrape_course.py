import json
from bs4 import BeautifulSoup
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

s = requests.Session()


def requests_retry_session(
    retries=3, backoff_factor=0.3, status_forcelist=(500, 502, 504), session=None
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def getCourseData(code, faculty):
    tia_url = "https://api.ntnu.no/rest/v4/emne/emnekode/194_"
    base_url_no = "https://www.ntnu.no/studier/emner/" + code
    data_no = requests_retry_session(session=s).get(url=base_url_no)
    soup_no = BeautifulSoup(data_no.text, "html5lib")
    # tia = requests.get(url=tia_url + code + "_1").text
    course_detail_h1 = "Ingen info for gitt studieår"
    try:
        course_detail_h1 = (
            soup_no.find_all("div", {"id": "course-details"})[0].h1.get_text().strip()
        )
    except IndexError:
        print("Something very wrong for course: " + code)
    if course_detail_h1 != "Ingen info for gitt studieår":
        base_url_eng = "https://www.ntnu.edu/studies/courses/" + code
        data_eng = requests_retry_session(session=s).get(url=base_url_eng)
        soup_eng = BeautifulSoup(data_eng.text, "html5lib")
        facts_about_course = ""
        try:
            facts_about_course = (
                soup_no.findAll("div", {"class": "card-body"})[1]
                .p.get_text()
                .split(":")
            )
        except IndexError:
            print("Cannot find facts about course at all, code " + code)
        credit = -1
        try:
            credit = float(facts_about_course[2].split("\n")[2][20:24])
        except ValueError:
            print("Not valid number, number is: ", facts_about_course[2].split("\n")[2])
        norwegian_name_raw = soup_no.title.get_text().split("-")
        norwegian_name = ""
        if len(norwegian_name_raw) > 4:
            norwegian_name = norwegian_name_raw[1][1 : len(norwegian_name_raw[1])]
            for i in range(2, len(norwegian_name_raw) - 4):
                norwegian_name += "-"
                norwegian_name += norwegian_name_raw[i]
            norwegian_name += "-"
            norwegian_name += norwegian_name_raw[len(norwegian_name_raw) - 3][
                0 : len(norwegian_name_raw[len(norwegian_name_raw) - 3]) - 1
            ]
        else:
            norwegian_name = norwegian_name_raw[1][1 : len(norwegian_name_raw[1]) - 1]
        english_name_raw = soup_eng.title.get_text().split("-")
        english_name = ""
        if len(english_name_raw) > 4:
            english_name = english_name_raw[1][1 : len(english_name_raw[1])]
            for i in range(2, len(english_name_raw) - 4):
                english_name += "-"
                english_name += english_name_raw[i]
            english_name += "-"
            english_name += english_name_raw[len(english_name_raw) - 3][
                0 : len(english_name_raw[len(english_name_raw) - 3]) - 1
            ]
        else:
            english_name = english_name_raw[1][1 : len(english_name_raw[1]) - 1]
        course_level_text = facts_about_course[3].split("\n")[0][
            1 : len(facts_about_course[3].split("\n")[0])
        ]
        study_level = course_level(course_level_text, code)
        last_year_taught = 0
        taught_from = 2008
        taught_in_autumn = False
        taught_in_spring = False
        taught_in_english = False
        undervisning = soup_no.find_all("div", {"class": "card-body"})[2]
        classes = undervisning.get_text().split("Undervises")
        place = ""
        try:
            place = undervisning.get_text().split("Sted:")[1].strip()
        except IndexError:
            print("Cannot get place")
        for elements in classes:
            if "HØST" in elements:
                taught_in_autumn = True
            if "VÅR" in elements:
                taught_in_spring = True
            if "Engelsk" in elements:
                taught_in_english = True
        content = None
        info_type = []
        exam_type = ""
        grade_type = ""
        try:
            exam_type_raw = (
                soup_no.find_all("div", {"class": "content-assessment"})[0]
                .p.contents[0]
                .strip()
                .split(":")[1]
            )
            exam_type = exam_type_raw[1 : len(exam_type_raw)]
        except IndexError:
            print("Cannot get exam type")
        try:
            grade_type_raw = (
                soup_no.find_all("div", {"class": "content-assessment"})[0]
                .p.contents[2]
                .strip()
                .split(":")[1]
            )
            grade_type = grade_type_raw[1 : len(grade_type_raw)]
        except IndexError:
            print("Cannot get exam type")
        try:
            content = soup_no.find_all("div", {"id": "course-content-toggler"})[
                0
            ].p.get_text()
            info_type.append({"code": "INNHOLD", "text": content})
        except IndexError:
            print("Cannot get content")
        learning_form = None
        try:
            learning_form = soup_no.find_all("div", {"id": "learning-method-toggler"})[
                0
            ].p.get_text()
            info_type.append({"code": "LÆRFORM", "text": learning_form})
        except IndexError:
            print("Cannot get learning from")
        learning_goal = None
        try:
            learning_goal = soup_no.find_all("div", {"id": "learning-goal-toggler"})[
                0
            ].p.get_text()
            info_type.append({"code": "MÅL", "text": learning_goal})
        except IndexError:
            print("Cannot get learning goal")

        course = {
            "course": {
                "norwegianName": norwegian_name,
                "englishName": english_name,
                "code": code,
                "credit": credit,
                "studyLevelCode": study_level,
                "lastYearTaught": last_year_taught,
                "taughtFromYear": taught_from,
                "taughtInAutumn": taught_in_autumn,
                "taughtInSpring": taught_in_spring,
                "taughtInEnglish": taught_in_english,
                "infoType": info_type,
                "examType": exam_type,
                "gradeType": grade_type,
                "place": place,
            }
        }
        return json.dumps(course)

    else:
        print("Grades.no - API - Fallback for course: " + code)
        base_url = "https://grades.no/api/courses/"
        resp = requests_retry_session(session=s).get(url=base_url + code)
        data = json.loads(resp.text) if resp.status_code == 200 else None
        if data and not "detail" in data:
            info_type = []
            if "content" in data:
                info_type.append({"code": "INNHOLD", "text": data["content"]})
            if "learning_form" in data:
                info_type.append({"code": "LÆRFORM", "text": data["learning_form"]})
            if "learning_goal" in data:
                info_type.append({"code": "MÅL", "text": data["learning_goal"]})
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
                    "infoType": info_type,
                    "examType": "",
                    "gradeType": "",
                    "place": "",
                }
            }
            return json.dumps(course)

        print("No information about course: " + code + " could be found - skipping")
        return None


def course_level(course_level_text, code):
    if course_level_text == "Doktorgrads nivå":
        return 900
    elif course_level_text == "Videreutdanning lavere grad":
        return 800
    elif course_level_text == "Høyere grads nivå":
        return 500
    elif course_level_text == "Fjerdeårsemner, nivå IV":
        return 400
    elif course_level_text == "Tredjeårsemner, nivå III":
        return 300
    elif course_level_text == "Videregående emner, nivå II":
        return 200
    elif course_level_text == "Grunnleggende emner, nivå I":
        return 100
    elif course_level_text == "Lavere grad, redskapskurs":
        return 90
    elif course_level_text == "Norsk for internasjonale studenter":
        return 80
    elif course_level_text == "Examen facultatum":
        return 71
    elif course_level_text == "Examen philosophicum":
        return 70
    elif course_level_text == "Forprøve/forkurs":
        return 60
    else:
        print(course_level_text, code)
        return -1

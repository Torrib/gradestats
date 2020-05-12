from django.db.models import TextChoices
import re

"""import json
import getpass
from bs4 import BeautifulSoup
from scripts.scrape_course import get_course_data
from scripts.course_is_digital import (
    course_has_digital_exam_semester,
    course_has_digital_exam,
)
"""

from grades.models import Grade, Course, Faculty, Department

from .feide import FeideClient


class MenuAction(TextChoices):
    DISTRIBUTION_OF_GRADES = 1, "Distribution of grades (FS580.001)"
    GRADE_DISTRIBUTION = 2, "Simple distribution of grades (FS581.001)"
    STATS_EXAM = 3, "Gradestatistics, exam (FS582.001)"
    STATS_COURSE = 4, "Creditstatistics per course - per level (FS581.002)"


class ExamSemester(TextChoices):
    SPRING = "VÅR", "Vår"
    SUMMER = "SOM", "Sommer"
    AUTUMN = "HØST", "Høst"


class KarstatClient(FeideClient):
    init_login_url = "https://innsida.ntnu.no/sso/?target=KarstatProd"
    base_url = "https://sats.itea.ntnu.no/karstat"
    exam_semesters = [ExamSemester.SPRING[0], ExamSemester.SUMMER[0], ExamSemester.AUTUMN[0]]
    language_code = "no"

    def login(self, username: str, password: str):
        result = super().login(username, password)
        self.session.post(self.get_language_url())
        return result

    def get_menu_url(self):
        return f"{self.base_url}/menuAction.do"

    def get_karstat_url(self):
        return f"{self.base_url}/fs582001Action.do"

    def get_language_url(self):
        return f"{self.base_url}/login.do?lang={self.language_code}"

    def get_faculty_url(self, faculty_key: int):
        return f"{self.get_menu_url()}?faculty={faculty_key}"

    def get_department_url(self, faculty_id: int, department_id: int):
        return f"{self.get_faculty_url(faculty_id)}&department={department_id}"

    def get_faculties_data(self):
        form_data = {
            "reportType": MenuAction.STATS_EXAM,
        }
        response = self.session.post(self.get_menu_url(), data=form_data)
        faculty_list_soup = self.init_soup(response.text)
        faculty_links = faculty_list_soup.select('a[href^="menuAction.do?faculty="]')

        faculty_link_pattern = re.compile(r'menuAction\.do\?faculty=(?P<faculty_key>\d{2})')
        faculties_data = []
        for link_tag in faculty_links:
            link = link_tag.get('href')
            faculty_key = faculty_link_pattern.match(link).groupdict().get('faculty_key')
            faculty_name = link_tag.get_text().strip()
            faculties_data.append({
                "key": faculty_key,
                "norwegian_name": faculty_name,
            })

        return faculties_data

    def get_departments_data(self, faculty_key: int):
        form_data = {
            "reportType": MenuAction.STATS_EXAM,
        }
        self.session.post(self.get_menu_url(), data=form_data)
        response = self.session.post(self.get_faculty_url(faculty_key))
        department_list_soup = self.init_soup(response.text)
        department_links = department_list_soup.select(f'a[href^="menuAction.do?faculty={faculty_key}&"]')

        department_link_pattern = re.compile(r'menuAction\.do\?faculty=(?P<faculty_key>\d{2})&department=(?P<department_key>\d{2})')
        departments_data = []
        for link_tag in department_links:
            link = link_tag.get('href')
            department_key = department_link_pattern.match(link).groupdict().get('department_key')
            department_name = link_tag.get_text().strip()
            departments_data.append({
                "key": department_key,
                "norwegian_name": department_name,
            })

        return departments_data

    def get_or_create_faculties(self):
        faculties_data = self.get_faculties_data()
        faculties = []
        for faculty_data in faculties_data:
            faculty, created = Faculty.objects.get_or_create(**faculty_data)
            faculties.append(faculty)
        return faculties

    def get_or_create_departments(self):
        departments = []
        for faculty in Faculty.objects.all():
            departments_data = self.get_departments_data(faculty.key)
            for department_data in departments_data:
                department, created = Department.objects.get_or_create(**department_data, faculty=faculty)
                departments.append(department)
        return departments

    def get_faculty(self, faculty_id: int):
        karstat_data = {
            "yearExam": "2013",
            "semesterExam": "HØST",
            "numberOfYears": "0",
            "minCandidates": "3",
        }
        self.session.get(self.get_faculty_url(faculty_id))

from django.db.models import TextChoices
import re

from grades.models import Grade, Course, Department, Semester

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
    language_code = "no"

    def login(self, username: str, password: str):
        result = super().login(username, password)
        self.session.post(self.get_language_url())
        return result

    def get_menu_url(self):
        return f"{self.base_url}/menuAction.do"

    def get_grade_report_url(self):
        return f"{self.base_url}/fs582001Action.do"

    def get_language_url(self):
        return f"{self.base_url}/login.do?lang={self.language_code}"

    def get_faculty_url(self, faculty_id: int):
        return f"{self.get_menu_url()}?faculty={faculty_id}"

    def get_department_url(self, faculty_id: int, department_id: int):
        return f"{self.get_faculty_url(faculty_id)}&department={department_id}"


class KarstatGradeClient(KarstatClient):
    @staticmethod
    def get_karstat_semester_name(semester: Semester):
        if semester == Semester.SPRING:
            return "VÅR"
        elif semester == Semester.SUMMER:
            return "SOM"
        elif semester == Semester.AUTUMN:
            return "HØST"

    def request_grade_reports_content(
        self, department: Department, year: int, semester: Semester
    ):
        form_data = {
            "reportType": MenuAction.STATS_EXAM,
        }
        # Navigate to the reports page
        self.session.post(self.get_menu_url(), data=form_data)

        faculty_id = department.faculty.faculty_id
        department_id = department.department_id
        department_url = self.get_department_url(faculty_id, department_id)

        # Navigate to the departments and faculties page.
        self.session.get(department_url)

        grade_report_form_data = {
            "yearExam": str(year),
            "semesterExam": str(self.get_karstat_semester_name(semester)),
            "numberOfYears": str(0),
            "minCandidates": str(3),
        }

        grade_reports_url = "https://sats.itea.ntnu.no/karstat/fs582001Action.do"
        grade_reports_page = self.session.post(
            grade_reports_url, data=grade_report_form_data
        )

        return grade_reports_page.text

    def parse_grade_report_page(
        self,
        page_content_text: str,
        department: Department,
        year: int,
        semester: Semester,
    ):
        page_content = self.init_soup(page_content_text)

        # Grade info
        rows_grades = page_content.find_all(class_="tableRow")

        grades_data = []

        # row 5 and down is subjects
        for i in range(0, len(rows_grades) - 1):

            td_grades = rows_grades[i].find_all("td")
            course_code = td_grades[0].string.split("-")[0].strip()
            course = Course.objects.filter(code=course_code).first()

            if not course:
                # TODO: _maybe_ handle courses which are not present in the DB yet in some way
                continue

            course.department = department
            course.save()

            attending = int(td_grades[5].string.strip())
            f = int(td_grades[6].string.strip())
            passing = attending - f

            a = round((int(td_grades[13].string.strip()) / 100.0) * passing)
            b = round((int(td_grades[14].string.strip()) / 100.0) * passing)
            c = round((int(td_grades[15].string.strip()) / 100.0) * passing)
            d = round((int(td_grades[16].string.strip()) / 100.0) * passing)
            e = round((int(td_grades[17].string.strip()) / 100.0) * passing)

            s = a + b + c + d + e + f

            passed = 0
            if s - f == 0:
                passed = passing

            if s == 0:
                average_grade = 0
            else:
                average_grade = (a * 5.0 + b * 4 + c * 3 + d * 2 + e) / s

            grade_data = {
                "course_id": course.id,
                "semester": str(semester),
                "year": year,
                "average_grade": average_grade,
                "passed": passed,
                "a": a,
                "b": b,
                "c": c,
                "d": d,
                "e": e,
                "f": f,
            }

            grades_data.append(grade_data)

        return grades_data

    def build_grades_from_data(self, grades_data):
        grades = []
        for grade_data in grades_data:
            course_id = grade_data.get("course_id")
            semester = grade_data.get("semester")
            year = grade_data.get("year")
            try:
                grade = Grade.objects.get(
                    course_id=course_id, semester=semester, year=year,
                )
                Grade.objects.filter(
                    course_id=course_id, semester=semester, year=year,
                ).update(**grade_data)
                grade.refresh_from_db()
            except Grade.DoesNotExist:
                grade = Grade.objects.create(**grade_data)

            grades.append(grade)

        return grades

    def update_grade_stats(self, department: Department, year: int, semester: Semester):
        report_page = self.request_grade_reports_content(
            department=department, year=year, semester=semester,
        )
        grades_data = self.parse_grade_report_page(
            report_page, department=department, year=year, semester=semester,
        )
        grades = self.build_grades_from_data(grades_data)
        # Convert to queryset to get annotations and aggregations
        grade_ids = [grade.id for grade in grades]
        grades = Grade.objects.filter(pk__in=grade_ids)
        return grades

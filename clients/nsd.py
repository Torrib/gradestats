from django.db.models import TextChoices
from json import JSONDecodeError

from .client import Client

from grades.models import Semester, Course, Grade

"""
API documentation can be found at:
https://dbh.nsd.uib.no/dbhvev/dokumenter/api/api_dokumentasjon.pdf
"""


class FilterType(TextChoices):
    TOP = "top", "Topp"
    ALL = "all", "Alle"
    ITEM = "item", "Enkelt enhet"
    BETWEEN = "between", "Mellom"
    LIKE = "like", "Lik"
    LESSTHAN = "lessthan", "Mindre enn"


class NSDGradeClient(Client):
    base_url = "https://api.nsd.no"
    api_version = 1
    table_id = 308
    status_line = False  # Should extra information about the API response be included?
    code_text = True  # Should names of related resources be included?
    decimal_separator = "."
    institution_id = 1150  # ID for NTNU in NSD databases

    def __init__(self):
        super().__init__()
        self.session.headers.update({"Content-type": "application/json"})

    def get_json_table_url(self):
        return f"{self.base_url}/dbhapitjener/Tabeller/hentJSONTabellData"

    def create_filter(self, name: str, filter_type: FilterType, values):
        return {
            "variabel": name,
            "selection": {"filter": filter_type, "values": values, "exclude": [""],},
        }

    def get_semester_id(self, semester: Semester):
        lookup = {
            Semester.SPRING: 1,
            Semester.SUMMER: 2,  # NSD does not actually work for SUMMER semester!
            Semester.AUTUMN: 3,
        }
        return lookup[semester]

    def get_semester_filter(self, semester: Semester):
        semester_id = self.get_semester_id(semester)
        return self.create_filter(
            name="Semester", filter_type=FilterType.ITEM, values=[semester_id]
        )

    def get_institution_filter(self):
        return self.create_filter(
            name="Institusjonskode",
            filter_type=FilterType.ITEM,
            values=[str(self.institution_id)],
        )

    def get_department_filter(self):
        return self.create_filter(
            name="Avdelingskode", filter_type=FilterType.ALL, values=["*"]
        )

    def get_course_filter(self, course_code: str):
        # Filter course code by SQL 'like' since course codes in NSD include a version number in the string.
        course_code_likeness = f"{course_code}-%"
        return self.create_filter(
            name="Emnekode", filter_type=FilterType.LIKE, values=[course_code_likeness]
        )

    def get_year_filter(self, year: int):
        return self.create_filter(
            name="Årstall", filter_type=FilterType.ITEM, values=[str(year)]
        )

    def get_field_of_study_filter(self):
        return self.create_filter(
            name="Studieprogramkode", filter_type=FilterType.ITEM, values=["*"]
        )

    def get_filters(self, course_code: str, year: int, semester: Semester):
        return [
            self.get_semester_filter(semester),
            self.get_institution_filter(),
            self.get_department_filter(),
            self.get_course_filter(course_code),
            self.get_year_filter(year),
            self.get_field_of_study_filter(),
        ]

    def build_query(self, course_code: str, year: int, semester: Semester, limit=1000):
        filters = self.get_filters(course_code, year, semester)
        query = {
            "tabell_id": self.table_id,
            "api_versjon": self.api_version,
            "statuslinje": "J" if self.status_line else "N",
            "begrensning": str(limit),
            "kodetekst": "J" if self.code_text else "N",
            "desimal_separator": self.decimal_separator,
            "groupBy": ["Institusjonskode", "Avdelingskode", "Emnekode", "Karakter"],
            "sortBy": ["Institusjonskode", "Avdelingskode"],
            "variabler": ["*"],
            "filter": filters,
        }
        return query

    def resolve_result_for_grade(self, results, letter: str):
        grade_results = [
            result for result in results if result.get("Karakter") == letter
        ]
        if len(grade_results) == 0:
            return 0
        elif len(grade_results) > 1:
            raise Exception("Found more than a single grade entry for a course")

        grade_result = grade_results[0]
        return int(grade_result.get("Antall kandidater totalt"))

    def build_grade_data_from_results(
        self, results, course_code: str, year: int, semester: Semester
    ):
        passed = self.resolve_result_for_grade(results, "G")
        failed = self.resolve_result_for_grade(results, "H")
        a = self.resolve_result_for_grade(results, "A")
        b = self.resolve_result_for_grade(results, "B")
        c = self.resolve_result_for_grade(results, "C")
        d = self.resolve_result_for_grade(results, "D")
        e = self.resolve_result_for_grade(results, "E")
        f = self.resolve_result_for_grade(results, "F")

        student_count = a + b + c + d + e + f

        is_pass_fail = any(map(lambda number: number != 0, [passed, failed]))
        is_graded = any(map(lambda number: number != 0, [a, b, c, d, e, f]))

        if is_pass_fail and is_graded:
            raise Exception("Course is both pass/fail and graded by letters")

        if is_pass_fail:
            data = {
                "passed": passed,
                "f": failed,
                "average_grade": 0,
            }
        else:
            average_grade = (a * 5.0 + b * 4 + c * 3 + d * 2 + e) / student_count
            data = {
                "a": a,
                "b": b,
                "c": c,
                "d": d,
                "e": e,
                "f": f,
                "average_grade": average_grade,
            }

        course = Course.objects.get(code=course_code)
        data.update(
            {"course_id": course.id, "semester": str(semester), "year": year,}
        )

        return data

    def build_grade_from_data(self, grade_data):
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

        return Grade.objects.get(pk=grade.id)

    def request_grade_data(self, course_code: str, year: int, semester: Semester):
        query = self.build_query(course_code, year, semester)
        url = self.get_json_table_url()
        response = self.session.post(url, json=query)
        try:
            results = response.json()
        except JSONDecodeError:
            results = []
        return results

    def update_grade(self, course_code: str, year: int, semester: Semester):
        results = self.request_grade_data(course_code, year, semester)
        if len(results) == 0:
            return None
        grade_data = self.build_grade_data_from_results(
            results, course_code, year, semester
        )
        grade = self.build_grade_from_data(grade_data)
        return grade

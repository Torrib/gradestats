import re

from grades.models import Course

from .feide import FeideClient


class TIAClient(FeideClient):
    init_login_url = "https://api.ntnu.no/rest/v4"
    base_url = "https://api.ntnu.no/rest/v4"

    "https://api.ntnu.no/rest/v4/studieprogram?limit=10000"
    @staticmethod
    def get_fs_course_code(course_code: str):
        institution_id = "194"
        course_version = "1"
        return f"{institution_id}_{course_code}_{course_version}"

    def get_url_for_course(self, course_code: str):
        fs_course_code = self.get_fs_course_code(course_code)
        return f"{self.base_url}/emne/emnekode/{fs_course_code}"

    def get_course_data(self, course_code: str):
        response = self.session.get(self.get_url_for_course(course_code))
        return response.json()

    def parse_term_code(self, term_code: str) -> [str, int]:
        """
        :param term_code: TIA term code e.g 2004_VÅR
        :return: (semester, year) e.g ('V', 2004)
        """
        semester_lookup = {
            "VÅR": 'V',
            "SOM": 'S',
            "HØST": 'H',
        }
        search_pattern = re.compile(r'(?P<year>\d{4})_(?P<semester>VÅR|SOM|HØST)')
        results = search_pattern.match(term_code).groupdict()
        semester = results.get("semester")
        year = results.get("year")
        return semester_lookup[semester], int(year)

    def resolve_course_role(self, course_roles: dict, key: str):
        role_list = course_roles.get(key, None)
        if role_list:
            term_code = role_list[0].get("actsOn").get("arsterminkode")
            return self.parse_term_code(term_code)
        return None, None

    def resolve_data_for_course_code(self, course_code: str):
        base_data = self.get_course_data(course_code)
        if not base_data.get("emne"):
            return None
        course_data = base_data.get("emne").get("fs_emne")

        course_names = course_data.get("name")
        norwegian_name = course_names.get("navn_nob")
        english_name = course_names.get("navn_eng")

        credit = course_data.get("studiepoeng")

        roles = course_data.get("roles")
        taught_from_semester, taught_from_year = self.resolve_course_role(roles, "forste_eksamen")
        last_year_taught_semester, last_year_taught_year = self.resolve_course_role(roles, "siste_eksamen")

        data = {
            "norwegian_name": norwegian_name,
            "english_name": english_name,
            "credit": credit,
            "taught_from": taught_from_year,
            "last_year_taught": last_year_taught_year,
        }

        return {k: v for k, v in data.items() if v is not None}

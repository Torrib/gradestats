import re

from grades.models import Course, Faculty, Department

from .feide import FeideClient


class TIAClient(FeideClient):
    init_login_url = "https://api.ntnu.no/rest/v4"
    base_url = "https://api.ntnu.no/rest/v4"
    model = None
    pk_field = None
    resource_name = None

    def get_detail_url(self, object_id):
        return ""

    def get_list_url(self, limit: int, skip: int):
        return ""

    def request_detail_content(self, object_id):
        response = self.session.get(self.get_detail_url(object_id))
        return response.json()

    def request_list_content(self, limit: int, skip: int):
        response = self.session.get(self.get_list_url(limit, skip))
        return response.json()

    def resolve_data_for_object(self, content: dict):
        data = {}
        return data

    def get_resource_from_content_root(self, content_root: dict):
        return content_root.get(self.resource_name)

    def get_object_data_detail(self, object_id):
        content = self.request_detail_content(object_id)
        obj = self.get_resource_from_content_root(content)
        object_data = self.resolve_data_for_object(obj)
        return {k: v for k, v in object_data.items() if v is not None}

    def get_object_data_list(self, limit: int, skip: int):
        content = self.request_list_content(limit, skip)
        objects = self.get_resource_from_content_root(content)
        objects_data = []
        for obj in objects:
            object_data = self.resolve_data_for_object(obj)
            objects_data.append({k: v for k, v in object_data.items() if v is not None})
        return objects_data

    def build_object_from_data(self, object_data: dict):
        object_pk = object_data.get(self.pk_field)
        try:
            query = {self.pk_field: object_pk}
            obj = self.model.objects.get(**query)
            self.model.objects.filter(**query).update(**object_data)
            obj.refresh_from_db()
        except self.model.DoesNotExist:
            obj = self.model.objects.create(**object_data)
        return obj

    def build_objects_from_data(self, objects_data):
        objects = []
        for object_data in objects_data:
            obj = self.build_object_from_data(object_data)
            objects.append(obj)
        return objects

    def refresh_object(self, object_pk):
        object_data = self.get_object_data_detail(object_pk)
        obj = self.build_object_from_data(object_data)
        return obj

    def refresh_objects(self, limit: int, skip: int):
        objects_data = self.get_object_data_list(limit, skip)
        objects = self.build_objects_from_data(objects_data)
        return objects

    class Meta:
        abstract = True


class TIACourseClient(TIAClient):
    model = Course
    pk_field = "code"
    resource_name = "emne"

    @staticmethod
    def get_fs_course_code(course_code: str):
        institution_id = "194"
        course_version = "1"
        return f"{institution_id}_{course_code}_{course_version}"

    def get_detail_url(self, object_id: int):
        return f"{self.base_url}/emne/emnekode/{object_id}"

    def get_list_url(self, limit: int, skip: int):
        return f"{self.base_url}/emne" f"?limit={limit}" f"&skip={skip}"

    def parse_term_code(self, term_code: str) -> [str, int]:
        """
        :param term_code: TIA term code e.g 2004_VÅR
        :return: (semester, year) e.g ('V', 2004)
        """
        semester_lookup = {
            "VÅR": "V",
            "SOM": "S",
            "HØST": "H",
        }
        search_pattern = re.compile(r"(?P<year>\d{4})_(?P<semester>VÅR|SOM|HØST)")
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

    def resolve_data_for_object(self, content: dict):
        data = super().resolve_data_for_object(content)
        course_data = content.get("fs_emne")

        code = course_data.get("emnekode")
        # Course codes with slashes don't work well as URLs.
        if code.find("/") >= 0:
            code = code.replace("/", "-")
        credit = course_data.get("studiepoeng")

        course_names = course_data.get("name")
        norwegian_name = course_names.get("navn_nob")
        english_name = course_names.get("navn_eng")

        roles = course_data.get("roles")
        taught_from_semester, taught_from_year = self.resolve_course_role(
            roles, "forste_eksamen"
        )
        last_year_taught_semester, last_year_taught_year = self.resolve_course_role(
            roles, "siste_eksamen"
        )

        data.update(
            {
                "code": code,
                "norwegian_name": norwegian_name,
                "english_name": english_name,
                "credit": credit,
                "taught_from": taught_from_year,
                "last_year_taught": last_year_taught_year,
            }
        )

        return data


class TIAOrganizationUnitClient(TIAClient):
    organization_type = None
    resource_name = "organisasjon"
    pk_field = "organization_unit_id"

    def get_detail_url(self, object_id: int):
        return f"{self.base_url}/organisasjon/ouid/{object_id}"

    def get_list_url(self, limit: int, skip: int):
        return (
            f"{self.base_url}/organisasjon"
            f"?limit={limit}"
            f"&skip={skip}"
            f"&filter=orgreg2_org.ouCategory={self.organization_type}"
        )

    def resolve_data_for_object(self, organization: dict):
        data = super().resolve_data_for_object(organization)
        fs_stedref = organization.get("fs_stedref")
        orgreg2b_org = organization.get("orgreg2b_org")
        if fs_stedref:
            names = fs_stedref.get("name")
        else:
            names = orgreg2b_org.get("name")
        acronym = names.get("akronym")
        norwegian_name = names.get("fullname_nob")
        english_name = names.get("fullname_eng")

        orgreg2_org = organization.get("orgreg2_org")
        organization_unit_id = orgreg2_org.get("ouId")
        nsd_code = orgreg2_org.get("nsdCodes")[0]

        data.update(
            {
                "acronym": acronym,
                "norwegian_name": norwegian_name,
                "english_name": english_name,
                "organization_unit_id": organization_unit_id,
                "nsd_code": nsd_code,
            }
        )
        return data

    class Meta:
        abstract = True


class TIAFacultyClient(TIAOrganizationUnitClient):
    organization_type = "Fakultet"
    model = Faculty

    def resolve_data_for_object(self, organization: dict):
        organization_data = super().resolve_data_for_object(organization)

        orgreg2_org = organization.get("orgreg2_org")
        faculty_id = orgreg2_org.get("facNr")

        organization_data.update(
            {"faculty_id": faculty_id,}
        )

        return organization_data


class TIADepartmentClient(TIAOrganizationUnitClient):
    organization_type = "Institutt"
    model = Department

    def resolve_data_for_object(self, organization: dict):
        organization_data = super().resolve_data_for_object(organization)

        orgreg2_org = organization.get("orgreg2_org")
        department_id = orgreg2_org.get("secNr")
        faculty_id = orgreg2_org.get("facNr")

        faculty = Faculty.objects.filter(faculty_id=faculty_id).first()

        organization_data.update(
            {
                "department_id": department_id,
                "faculty_id": faculty.id if faculty else None,
            }
        )

        return organization_data

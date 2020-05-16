import re

from grades.models import Course

from .client import Client


class CoursePagesClient(Client):
    base_url = "https://www.ntnu.no/studier/emner"
    base_url_eng = "https://www.ntnu.edu/studies/courses"

    def get_course_url(self, course_code: str):
        return f"{self.base_url}/{course_code}"

    def parse_card_content_by_title(self, soup, title: str):
        card_title = soup.find("div", {"class": "card-header"}, string=title)
        facts_card = card_title.parent
        card_body = facts_card.find("div", {"class": "card-body"})

        content_text = card_body.get_text()
        search_pattern = re.compile(r"(?P<name>\S+):(\s+)(?P<value>(\S| )+)")
        results = search_pattern.finditer(self.normalize(content_text))

        content = {}
        for match in results:
            groupdict = match.groupdict()
            key = groupdict.get("name")
            value = groupdict.get("value")
            content[key] = value
        return content

    @staticmethod
    def get_study_level_from_description(description: str):
        if description == "Doktorgrads nivå":
            return 900
        elif description == "Videreutdanning lavere grad":
            return 800
        elif description == "Høyere grads nivå":
            return 500
        elif description == "Fjerdeårsemner, nivå IV":
            return 400
        elif description == "Tredjeårsemner, nivå III":
            return 300
        elif description == "Videregående emner, nivå II":
            return 200
        elif description == "Grunnleggende emner, nivå I":
            return 100
        elif description == "Lavere grad, redskapskurs":
            return 90
        elif description == "Norsk for internasjonale studenter":
            return 80
        elif description == "Examen facultatum":
            return 71
        elif description == "Examen philosophicum":
            return 70
        elif description == "Forprøve/forkurs":
            return 60
        else:
            return -1

    @staticmethod
    def normalize(string: str):
        return string.replace("\xa0\xc2", " ").replace("\xc2", " ").replace("\xa0", " ")

    def request_course_page(self, course_code: str):
        course_url = self.get_course_url(course_code)
        page_response = self.session.get(course_url)
        page_text = self.normalize(page_response.text)
        page_soup = self.init_soup(page_text)

        no_content_title = "Ingen info for gitt studieår"
        page_title = (
            page_soup.find("div", {"id": "course-details"}).h1.get_text().strip()
        )

        if page_title == no_content_title:
            return None

        facts_title_no = "Fakta om emnet"
        facts = self.parse_card_content_by_title(page_soup, facts_title_no)

        course_version = facts.get("Versjon")
        credits_string = facts.get("Studiepoeng")
        course_level_description = facts.get("Studienivå")
        study_level = self.get_study_level_from_description(course_level_description)

        last_year_taught = 0
        taught_from = 2008

        education = self.parse_card_content_by_title(page_soup, "Undervisning")
        language = education.get("Undervisningsspråk")
        taught_in_english = language == "Engelsk"

        term: str = education.get("Undervises")
        taught_in_spring = True if "VÅR" in term else None
        taught_in_autumn = True if "HØST" in term else None

        place = education.get("Sted")

        content = page_soup.find("div", {"id": "course-content-toggler"}).p.get_text()
        learning_form = page_soup.find(
            "div", {"id": "learning-method-toggler"}
        ).p.get_text()
        learning_goal = page_soup.find(
            "div", {"id": "learning-goal-toggler"}
        ).p.get_text()

        data = {
            "study_level": study_level,
            "taught_in_english": taught_in_english,
            "taught_in_autumn": taught_in_autumn,
            "taught_in_spring": taught_in_spring,
            "place": place,
            "content": content,
            "learning_form": learning_form,
            "learning_goal": learning_goal,
        }

        return {k: v for k, v in data.items() if v is not None}

    def update_course(self, course_code: str):
        course_data = self.request_course_page(course_code)
        Course.objects.filter(code=course_code).update(**course_data)

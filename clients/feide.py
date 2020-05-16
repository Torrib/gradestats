import re
from bs4 import BeautifulSoup
import requests

from grades.models import Course


class FeideClient:
    login_url = "https://idp.feide.no/simplesaml/module.php/feide/login.php"
    init_login_url = ""
    session = None

    def __init__(self):
        super().__init__()
        self.session = requests.session()

    def init_soup(self, page_text: str):
        return BeautifulSoup(page_text, "html5lib")

    def login(self, username: str, password: str):
        login_form_data = dict(
            feidename=username, password=password, org="ntnu.no", asLen="255"
        )
        feide_sso_page = self.session.get(self.init_login_url)

        sso_page_soup = self.init_soup(feide_sso_page.text)

        sso_form = sso_page_soup.find("form", {"name": "f"})
        auth_state = sso_form.find("input", {"name": "AuthState"}).get("value")

        login_form_data["AuthState"] = auth_state
        login_form_action = sso_form["action"]
        login_url = self.login_url + login_form_action

        login_response = self.session.post(login_url, data=login_form_data)
        login_response_soup = self.init_soup(login_response.text)

        saml_response_input = login_response_soup.find(
            "input", {"name": "SAMLResponse"}
        )
        relay_state_input = login_response_soup.find("input", {"name": "RelayState"})

        sso_confirm_data = {
            "SAMLResponse": saml_response_input.get("value"),
            "RelayState": relay_state_input.get("value") if relay_state_input else None,
        }
        sso_confirm_url = login_response_soup.find("form").get("action")
        self.session.post(sso_confirm_url, data=sso_confirm_data)

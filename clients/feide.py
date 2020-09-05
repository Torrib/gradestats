from .client import Client


class FeideClient(Client):
    login_url = "https://idp.feide.no/simplesaml/module.php/feide/login"
    init_login_url = ""

    def login(self, username: str, password: str):
        login_form_data = dict(
            feidename=username, password=password, has_js=0, inside_iframe=0
        )
        feide_sso_page = self.session.get(self.init_login_url)

        sso_page_soup = self.init_soup(feide_sso_page.text)

        auth_state = sso_page_soup.find("input", {"name": "AuthState"}).get("value")
        login_org = sso_page_soup.find("input", {"name": "org"}).get("value")

        login_url = f"{self.login_url}?org={login_org}&AuthState={auth_state}"

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

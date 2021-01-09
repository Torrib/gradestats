from django.contrib.auth.models import User
from mozilla_django_oidc.auth import OIDCAuthenticationBackend


def resolve_names(full_name: str):
    names = full_name.split(" ")
    if len(names) < 2:
        return None, None
    last_name = names.pop()
    first_name = " ".join(names)
    return first_name, last_name


class OIDCUserAuthenticationBackend(OIDCAuthenticationBackend):
    def create_user(self, claims):
        user: User = super().create_user(claims)
        user.first_name, user.last_name = resolve_names(claims.get("name"))
        user.save()
        return user

    def update_user(self, user: User, claims: dict):
        user.first_name, user.last_name = resolve_names(claims.get("name"))
        user.save()
        return user

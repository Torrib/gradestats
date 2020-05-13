from rest_framework.permissions import DjangoModelPermissions

_perms_map_with_view_perms = {
    "GET": ["%(app_label)s.view_%(model_name)s"],
    "OPTIONS": [],
    "HEAD": [],
    "POST": [],
    "PUT": ["%(app_label)s.change_%(model_name)s"],
    "PATCH": ["%(app_label)s.change_%(model_name)s"],
    "DELETE": ["%(app_label)s.delete_%(model_name)s"],
}


class DjangoModelPermissionOrAnonCreateOnly(DjangoModelPermissions):
    """
    Allow anyone to create a model, while require changing and viewing to have model permission.
    """

    authenticated_users_only = False
    perms_map = _perms_map_with_view_perms

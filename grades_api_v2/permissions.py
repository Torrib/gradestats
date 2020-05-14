from rest_framework import permissions

_perms_map_with_view_perms = {
    "GET": ["%(app_label)s.view_%(model_name)s"],
    "OPTIONS": [],
    "HEAD": [],
    "POST": [],
    "PUT": ["%(app_label)s.change_%(model_name)s"],
    "PATCH": ["%(app_label)s.change_%(model_name)s"],
    "DELETE": ["%(app_label)s.delete_%(model_name)s"],
}


class DjangoModelPermissionOrAnonCreateOnly(permissions.DjangoModelPermissions):
    """
    Allow anyone to create a model, while require changing and viewing to have model permission.
    """

    authenticated_users_only = False
    perms_map = _perms_map_with_view_perms


class IsAuthenticatedOrReadOnlyOrIsAdminUserOrOwnerEdit(
    permissions.IsAuthenticatedOrReadOnly
):
    """
    Allow anyone to read.
    Allow authenticated to create.
    Allow admin or creator to update or delete.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        if request.method == "GET":
            return True
        return bool(user and user.is_staff) or obj.created_by == user

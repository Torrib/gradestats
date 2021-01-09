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


class IsAdminUserOrReadOnly(permissions.BasePermission):
    """
    The requesting user is an admin, or is a read-only request.
    """

    def has_permission(self, request, view):
        return bool(
            request.method in permissions.SAFE_METHODS
            or request.user
            and request.user.is_staff
        )


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


class UserViewPermission(permissions.IsAuthenticated):
    """
    Allow authenticated to read.
    Allow none to create.
    Allow admin or creator to update.
    Allow admin to delete.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        if request.method == "GET":
            return user.is_authenticated
        elif request.method == "POST":
            return False
        elif request.method in ["PUT", "PATCH"]:
            return user.is_staff or obj == user
        elif request.method == "DELETE":
            return user.is_staff
        return False

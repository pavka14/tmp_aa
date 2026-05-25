from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsSuperUser(BasePermission):
    """
    Allow access only to superusers.

    This is a temporary demo-grade permission class — it grants blanket write
    access to any superuser and denies it to everyone else.  It is intentionally
    simple for proof-of-concept purposes.

    A production-grade implementation should use fine-grained group/role
    permissions so that different user roles (e.g. "Network Engineers") can be
    granted specific object-level or action-level privileges without requiring
    full superuser status.  See PRD — Limitations for details.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)


class IsSuperUserOrReadOnly(BasePermission):
    """
    Allow read-only access to any authenticated user; restrict write operations
    (POST, PUT, PATCH, DELETE) to superusers only.

    Delegates the superuser check to ``IsSuperUser`` so there is a single
    source of truth for that logic.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return bool(request.user and request.user.is_authenticated)
        return IsSuperUser().has_permission(request, view)

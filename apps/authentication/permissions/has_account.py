from rest_framework import permissions


class HasAccount(permissions.BasePermission):

    def has_permission(self, request, view):
        return hasattr(request, "account")

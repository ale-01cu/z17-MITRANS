from rest_framework import permissions
from .models import UserAccount


class IsSuperUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser


class IsManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'manager'


class IsConsultant(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'consultant'
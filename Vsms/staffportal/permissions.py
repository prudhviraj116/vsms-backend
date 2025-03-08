# myapp/permissions.py

from rest_framework.permissions import BasePermission

class IsStaff(BasePermission):
    """
    Allows access only to staff users.
    """
    def has_permission(self, request, view):
        return request.user and request.user.user_type == '2'  # '2' for Staff

class IsStudent(BasePermission):
    """
    Allows access only to student users.
    """
    def has_permission(self, request, view):
        return request.user and request.user.user_type == '3'  # '3' for Student

class IsStaffOrStudent(BasePermission):
    """
    Allows access to staff or student users.
    """
    def has_permission(self, request, view):
        return request.user and request.user.user_type in ['2', '3']  # '2' for Staff, '3' for Student

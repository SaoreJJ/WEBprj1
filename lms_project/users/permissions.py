from rest_framework import permissions


class IsModerator(permissions.BasePermission):
    """
    Проверяет, является ли пользователь модератором
    """
    def has_permission(self, request, view):
        return request.user.groups.filter(name='moderators').exists()


class IsOwner(permissions.BasePermission):
    """
    Проверяет, является ли пользователь владельцем объекта
    """
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsOwnerProfile(permissions.BasePermission):
    """
    Проверяет, является ли пользователь владельцем профиля
    """
    def has_object_permission(self, request, view, obj):
        return obj == request.user
from rest_framework import permissions


class UserPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        if request.user.id != obj.id:
            return False
        return True


class BuyerPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.role != 'buyer':
            return False
        return True


class SellerPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == 'POST':
            if request.user.role != 'seller':
                return False
        return True

    def has_object_permission(self, request, view, obj):
        if request.method != 'GET':
            if request.user.id != obj.seller.id:
                return False
        return True

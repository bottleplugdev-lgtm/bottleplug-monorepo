from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner of the object.
        return obj == request.user


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners or admins to access an object.
    """
    
    def has_object_permission(self, request, view, obj):
        # Admins can do anything
        if request.user.is_staff or request.user.user_type == 'admin':
            return True
        
        # Owners can access their own objects
        return obj == request.user


class IsDriverOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow drivers or admins to access driver-specific endpoints.
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.user_type == 'driver' or 
            request.user.is_staff or 
            request.user.user_type == 'admin'
        )


class IsCustomerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow customers or admins to access customer-specific endpoints.
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.user_type == 'customer' or 
            request.user.is_staff or 
            request.user.user_type == 'admin'
        ) 
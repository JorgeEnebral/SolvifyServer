from rest_framework.permissions import BasePermission, SAFE_METHODS 
    
class IsUnregisteredUser(BasePermission):
    """
    Permite registrarse solo a los usuarios que no están registrados.
    """

    def has_permission(self, request, view):
        return not request.user.is_authenticated and not request.user.is_staff
from rest_framework.permissions import BasePermission, SAFE_METHODS 
 
class IsOwnerOrAdmin(BasePermission): 
    """ 
    Permite editar/eliminar una subasta solo si el usuario es el propietario 
    o es administrador. Cualquiera puede consultar (GET). 
    """ 
 
    def has_object_permission(self, request, view, obj): 
        # Permitir acceso de lectura a cualquier usuario (GET, HEAD, OPTIONS) 
        if request.method in SAFE_METHODS: 
            return True 
        
        owner_fields = ['author', 'bidder']
        for field in owner_fields:
            if hasattr(obj, field):
                return getattr(obj, field) == request.user or request.user.is_staff
            
        # Permitir si el usuario es el creador o es administrador 
        return obj.bidder == request.user or request.user.is_staff
    
class IsOwnerOrAdminAuction(BasePermission): 
    """ 
    Permite editar/eliminar una subasta solo si el usuario es el propietario 
    o es administrador. Cualquiera puede consultar (GET). 
    """ 
 
    def has_object_permission(self, request, view, obj): 
        # Permitir acceso de lectura a cualquier usuario (GET, HEAD, OPTIONS) 
        if request.method in SAFE_METHODS: 
            return True 
 
        # Permitir si el usuario es el creador o es administrador 
        return obj.auctioneer == request.user or request.user.is_staff
    

class IsRegisteredUserOrAdmin(BasePermission):
    """
    Permite crear/editar/eliminar una subasta solo si el usuario está registrado
    o es administrador. Cualqueira puede consultar (GET).
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        
        return request.user.is_authenticated or request.user.is_staff
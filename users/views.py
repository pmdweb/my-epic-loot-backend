from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

@api_view(["GET"])
@permission_classes([IsAuthenticatedOrReadOnly])
def me(request):
    """Simple health endpoint for Users app."""
    user = request.user if request.user.is_authenticated else None
    return Response({"authenticated": bool(user), "username": getattr(user, "username", None)})

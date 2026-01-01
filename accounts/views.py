from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from drf_spectacular.utils import extend_schema

from .serializers import LoginRequestSerializer, LoginResponseSerializer


@extend_schema(
    request=LoginRequestSerializer,
    responses={200: LoginResponseSerializer},
    description="Obtain an auth token using username/password. Use it as: Authorization: Token <token>",
)
@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    serializer = LoginRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    username = serializer.validated_data["username"]
    password = serializer.validated_data["password"]

    user = authenticate(username=username, password=password)
    if not user:
        return Response({"detail": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

    token, _ = Token.objects.get_or_create(user=user)
    return Response({"token": token.key, "user_id": user.id, "username": user.username})


@extend_schema(
    request=None,
    responses={200: None},
    description="Invalidate the current token.",
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request):
    Token.objects.filter(user=request.user).delete()
    return Response({"detail": "Logged out"})

from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import CustomTokenObtainPairSerializer, RegisterSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom login view with email-based authentication."""

    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = (AllowAny,)


class RegisterView(generics.CreateAPIView):
    """User registration endpoint."""

    serializer_class = RegisterSerializer
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            {
                "message": "User registered successfully",
                "user_id": user.id,
                "email": user.email,
            },
            status=status.HTTP_201_CREATED,
        )


class ProfileView(generics.RetrieveAPIView):
    """Get current user profile."""

    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        from .serializers import UserSerializer

        return UserSerializer

    def get_object(self):
        return self.request.user
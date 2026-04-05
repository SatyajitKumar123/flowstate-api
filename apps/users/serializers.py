from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_bytes
from rest_framework import serializers


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        token["email"] = user.email
        token["first_name"] = user.first_name
        
        return token

class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)

    def create(self, validated_data):
        from apps.users.models import User
        
        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
        )
        return user
    
class UserSerializer(serializers.ModelSerializer):
    """Serializer for user profile."""

    class Meta:
        from apps.users.models import User

        model = User
        fields = ("id", "email", "first_name", "last_name", "phone_number", "created_at")
        read_only_fields = ("id", "created_at")

class PasswordResetRequestSerializer(serializers.Serializer):
    """Request password reset email."""

    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        from apps.users.models import User
        
        if not User.objects.filter(email=value).exists():
            return value
        return value
    
    def save(self):
        from apps.users.models import User
        
        email = self.validated_data["email"]
        user = User.objects.filter(email=email).first()
        
        if user:
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_decode(force_bytes(user.pk))
            reset_url = f"http://localhost:3000/reset-password/{uid}/{token}/"

            send_mail(
                subject="Password Reset Request",
                message=f"Click here to reset your password: {reset_url}",
                from_email="noreply@flowstate.dev",
                recipient_list=[user.email],
                fail_silently=False,
            )
            
class PasswordResetConfirmSerializer(serializers.Serializer):
    """Confirm password reset with token."""

    uid = serializers.CharField(required=True)
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8, write_only=True)

    def validate(self, data):
        from django.contrib.auth.tokens import default_token_generator
        from django.utils.http import urlsafe_base64_decode
        from apps.users.models import User
        
        try:
            uid = urlsafe_base64_decode(data["uid"]).decode()
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError):
            raise serializers.ValidationError("Invalid token or user ID")

        if not default_token_generator.check_token(user, data["token"]):
            raise serializers.ValidationError("Invalid or expired token")

        self.user = user
        return data

    def save(self):
        self.user.set_password(self.validated_data["new_password"])
        self.user.save()
        return self.user
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
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

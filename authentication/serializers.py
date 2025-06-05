from rest_framework import serializers
from django.contrib.auth.models import User


class LoginSerializer(serializers.Serializer):
    """
    Сериализатор для авторизации пользователя.
    """
    
    username = serializers.CharField(
        max_length=150,
        help_text="Имя пользователя"
    )
    password = serializers.CharField(
        write_only=True,
        help_text="Пароль пользователя"
    )


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для пользователя.
    """
    
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_active',
            'date_joined',
            'last_login'
        ]
        read_only_fields = [
            'id',
            'is_active',
            'date_joined',
            'last_login'
        ] 
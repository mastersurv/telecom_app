from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .serializers import LoginSerializer, UserSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    API endpoint для авторизации пользователя и получения JWT токена.
    
    Принимает username и password, возвращает access и refresh токены.
    """
    
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    username = serializer.validated_data['username']
    password = serializer.validated_data['password']
    
    user = authenticate(username=username, password=password)
    
    if user is None:
        return Response({
            'error': 'Неверные учетные данные'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    if not user.is_active:
        return Response({
            'error': 'Аккаунт пользователя деактивирован'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    refresh = RefreshToken.for_user(user)
    
    user_serializer = UserSerializer(user)
    
    return Response({
        'message': 'Успешная авторизация',
        'user': user_serializer.data,
        'tokens': {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token(request):
    """
    API endpoint для обновления access токена с помощью refresh токена.
    """
    
    refresh_token = request.data.get('refresh')
    
    if not refresh_token:
        return Response({
            'error': 'Refresh токен не предоставлен'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        refresh = RefreshToken(refresh_token)
        return Response({
            'access': str(refresh.access_token),
        }, status=status.HTTP_200_OK)
    except Exception:
        return Response({
            'error': 'Недействительный refresh токен'
        }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
def profile(request):
    """
    API endpoint для получения профиля текущего пользователя.
    """
    
    user_serializer = UserSerializer(request.user)
    
    return Response({
        'user': user_serializer.data
    }, status=status.HTTP_200_OK)

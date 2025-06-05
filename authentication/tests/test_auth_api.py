"""
Тесты для API аутентификации.
Покрывают JWT токены, валидацию и безопасность.
"""

import pytest
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import timedelta
from django.utils import timezone

from tests.factories import UserFactory

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.api
class TestUserLoginAPI:
    """Тесты для API входа пользователей."""
    
    def test_successful_login(self, api_client):
        """Тест успешного входа пользователя."""
        user = UserFactory(username='testuser')
        user.set_password('testpassword123')
        user.save()
        
        login_url = reverse('authentication:login')
        data = {
            'username': 'testuser',
            'password': 'testpassword123'
        }
        
        response = api_client.post(login_url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'tokens' in response.data
        assert 'user' in response.data
        assert 'message' in response.data
        
        # Проверяем структуру токенов
        tokens = response.data['tokens']
        assert 'access' in tokens
        assert 'refresh' in tokens
        
        # Проверяем информацию о пользователе
        user_data = response.data['user']
        assert user_data['id'] == user.id
        assert user_data['username'] == user.username
        assert user_data['email'] == user.email
        assert 'password' not in user_data  # Пароль не должен возвращаться
    
    def test_login_invalid_username(self, api_client):
        """Тест входа с несуществующим пользователем."""
        login_url = reverse('authentication:login')
        data = {
            'username': 'nonexistent',
            'password': 'testpassword123'
        }
        
        response = api_client.post(login_url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert 'error' in response.data
        assert response.data['error'] == 'Неверные учетные данные'
    
    def test_login_invalid_password(self, api_client):
        """Тест входа с неверным паролем."""
        user = UserFactory(username='testuser')
        user.set_password('testpassword123')
        user.save()
        
        login_url = reverse('authentication:login')
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        
        response = api_client.post(login_url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert 'error' in response.data
        assert response.data['error'] == 'Неверные учетные данные'
    
    def test_login_missing_username(self, api_client):
        """Тест входа без указания имени пользователя."""
        login_url = reverse('authentication:login')
        data = {
            'password': 'testpassword123'
        }
        
        response = api_client.post(login_url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'username' in response.data
    
    def test_login_missing_password(self, api_client):
        """Тест входа без указания пароля."""
        login_url = reverse('authentication:login')
        data = {
            'username': 'testuser'
        }
        
        response = api_client.post(login_url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password' in response.data
    
    def test_login_empty_credentials(self, api_client):
        """Тест входа с пустыми учетными данными."""
        login_url = reverse('authentication:login')
        data = {
            'username': '',
            'password': ''
        }
        
        response = api_client.post(login_url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'username' in response.data
        assert 'password' in response.data
    
    def test_login_inactive_user(self, api_client):
        """Тест входа неактивного пользователя."""
        user = UserFactory(username='testuser', is_active=False)
        user.set_password('testpassword123')
        user.save()
        
        login_url = reverse('authentication:login')
        data = {
            'username': 'testuser',
            'password': 'testpassword123'
        }
        
        response = api_client.post(login_url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert 'error' in response.data
        assert response.data['error'] == 'Неверные учетные данные'
    
    def test_login_case_sensitive_username(self, api_client):
        """Тест что имя пользователя чувствительно к регистру."""
        user = UserFactory(username='testuser')
        user.set_password('testpassword123')
        user.save()
        
        login_url = reverse('authentication:login')
        data = {
            'username': 'TESTUSER',  # Разный регистр
            'password': 'testpassword123'
        }
        
        response = api_client.post(login_url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
@pytest.mark.api
class TestJWTTokenValidation:
    """Тесты для валидации JWT токенов."""
    
    def test_access_token_structure(self):
        """Тест структуры access токена."""
        user = UserFactory()
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        
        # Проверяем что токен состоит из трех частей (header.payload.signature)
        parts = access_token.split('.')
        assert len(parts) == 3
        
        # Проверяем что каждая часть не пустая
        for part in parts:
            assert len(part) > 0
    
    def test_refresh_token_structure(self):
        """Тест структуры refresh токена."""
        user = UserFactory()
        refresh = RefreshToken.for_user(user)
        refresh_token = str(refresh)
        
        # Проверяем что токен состоит из трех частей
        parts = refresh_token.split('.')
        assert len(parts) == 3
    
    def test_token_authentication_success(self, api_client):
        """Тест успешной аутентификации с токеном."""
        user = UserFactory()
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        
        # Делаем запрос с токеном
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        # Используем любой защищенный endpoint
        url = reverse('equipment:equipment-list-create')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_token_authentication_invalid_token(self, api_client):
        """Тест аутентификации с невалидным токеном."""
        invalid_token = 'invalid.jwt.token'
        
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {invalid_token}')
        
        url = reverse('equipment:equipment-list-create')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_token_authentication_missing_bearer(self, api_client):
        """Тест аутентификации без префикса Bearer."""
        user = UserFactory()
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        
        # Отправляем токен без Bearer
        api_client.credentials(HTTP_AUTHORIZATION=access_token)
        
        url = reverse('equipment:equipment-list-create')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_token_authentication_no_token(self, api_client):
        """Тест обращения к защищенному endpoint без токена."""
        url = reverse('equipment:equipment-list-create')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_token_authentication_empty_token(self, api_client):
        """Тест аутентификации с пустым токеном."""
        api_client.credentials(HTTP_AUTHORIZATION='Bearer ')
        
        url = reverse('equipment:equipment-list-create')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
@pytest.mark.api
class TestAuthPermissions:
    """Тесты для проверки разрешений аутентификации."""
    
    def test_regular_user_access_to_equipment_api(self, api_client):
        """Тест доступа обычного пользователя к API оборудования."""
        user = UserFactory(is_staff=False, is_superuser=False)
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        url = reverse('equipment:equipment-list-create')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_staff_user_access_to_equipment_api(self, api_client):
        """Тест доступа staff пользователя к API оборудования."""
        user = UserFactory(is_staff=True, is_superuser=False)
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        url = reverse('equipment:equipment-list-create')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_super_user_access_to_equipment_api(self, api_client):
        """Тест доступа суперпользователя к API оборудования."""
        user = UserFactory(is_staff=True, is_superuser=True)
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        url = reverse('equipment:equipment-list-create')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_unauthenticated_access_blocked(self, api_client):
        """Тест что неаутентифицированный доступ заблокирован."""
        protected_urls = [
            reverse('equipment:equipment-list-create'),
            reverse('equipment:equipment-type-list'),
            reverse('equipment:equipment-stats'),
        ]
        
        for url in protected_urls:
            response = api_client.get(url)
            assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
@pytest.mark.api
class TestAuthErrorHandling:
    """Тесты для обработки ошибок аутентификации."""
    
    def test_malformed_jwt_token(self, api_client):
        """Тест обработки поврежденного JWT токена."""
        malformed_tokens = [
            'Bearer not.a.jwt',
            'Bearer incomplete.jwt',
            'Bearer too.many.parts.in.jwt.token',
            'Bearer header.only',
            'Bearer ..',
            'Bearer .',
        ]
        
        url = reverse('equipment:equipment-list-create')
        
        for token in malformed_tokens:
            api_client.credentials(HTTP_AUTHORIZATION=token)
            response = api_client.get(url)
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_tampered_jwt_token(self, api_client):
        """Тест обработки подделанного JWT токена."""
        user = UserFactory()
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        
        # Изменяем последний символ (подпись)
        tampered_token = access_token[:-1] + 'X'
        
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {tampered_token}')
        
        url = reverse('equipment:equipment-list-create')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_jwt_with_nonexistent_user(self, api_client):
        """Тест JWT токена для несуществующего пользователя."""
        user = UserFactory()
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        
        # Удаляем пользователя
        user.delete()
        
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        url = reverse('equipment:equipment-list-create')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
@pytest.mark.integration
class TestAuthIntegration:
    """Интеграционные тесты аутентификации."""
        
    def test_full_auth_flow(self, api_client):
        """Тест полного цикла аутентификации."""
        # 1. Создаем пользователя
        user = UserFactory(username='integrationuser')
        user.set_password('testpass123')
        user.save()
        
        # 2. Логинимся
        login_url = reverse('authentication:login')
        login_data = {
            'username': 'integrationuser',
            'password': 'testpass123'
        }
        
        login_response = api_client.post(login_url, login_data, format='json')
        assert login_response.status_code == status.HTTP_200_OK
        
        access_token = login_response.data['tokens']['access']
        
        # 3. Используем токен для доступа к API
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        equipment_url = reverse('equipment:equipment-list-create')
        equipment_response = api_client.get(equipment_url)
        assert equipment_response.status_code == status.HTTP_200_OK
        
        # 4. Проверяем что без токена доступ запрещен
        api_client.credentials()
        
        no_auth_response = api_client.get(equipment_url)
        assert no_auth_response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_concurrent_user_sessions(self, api_client):
        """Тест одновременных сессий пользователей."""
        user1 = UserFactory(username='user1')
        user1.set_password('pass1')
        user1.save()
        
        user2 = UserFactory(username='user2')
        user2.set_password('pass2')
        user2.save()
        
        login_url = reverse('authentication:login')
        
        # Логин первого пользователя
        login_data1 = {'username': 'user1', 'password': 'pass1'}
        response1 = api_client.post(login_url, login_data1, format='json')
        token1 = response1.data['tokens']['access']
        
        # Логин второго пользователя
        login_data2 = {'username': 'user2', 'password': 'pass2'}
        response2 = api_client.post(login_url, login_data2, format='json')
        token2 = response2.data['tokens']['access']
        
        # Проверяем что оба токена работают
        equipment_url = reverse('equipment:equipment-list-create')
        
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token1}')
        response = api_client.get(equipment_url)
        assert response.status_code == status.HTTP_200_OK
        
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token2}')
        response = api_client.get(equipment_url)
        assert response.status_code == status.HTTP_200_OK 
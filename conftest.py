"""
Конфигурация pytest для Django проекта
"""
import os
import django
import pytest


def pytest_configure(config):
    """
    Настройка pytest для Django
    """
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'telecom_backend.settings_test')
    django.setup()


@pytest.fixture
def api_client():
    """
    Клиент для API тестов
    """
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def admin_user(django_user_model):
    """
    Создает суперпользователя для тестов
    """
    return django_user_model.objects.create_superuser(
        username='admin',
        email='admin@test.com',
        password='admin123'
    )


@pytest.fixture
def regular_user(django_user_model):
    """
    Создает обычного пользователя для тестов
    """
    return django_user_model.objects.create_user(
        username='user',
        email='user@test.com',
        password='user123'
    )


@pytest.fixture
def authenticated_client(api_client, regular_user):
    """
    Аутентифицированный клиент
    """
    from rest_framework_simplejwt.tokens import RefreshToken
    
    refresh = RefreshToken.for_user(regular_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


@pytest.fixture
def admin_client(api_client, admin_user):
    """
    Аутентифицированный админ клиент
    """
    from rest_framework_simplejwt.tokens import RefreshToken
    
    refresh = RefreshToken.for_user(admin_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client 
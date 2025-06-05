#!/usr/bin/env python
"""
Скрипт для запуска всех тестов с покрытием кода
"""
import os
import django
import pytest

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'telecom_backend.settings_test')
django.setup()

if __name__ == '__main__':
    # Запуск всех тестов с покрытием кода
    pytest.main([
        '-v',
        '--cov=equipment',
        '--cov=authentication', 
        '--cov=telecom_backend',
        '--cov-report=term-missing',
        '--cov-report=html:htmlcov',
        '--tb=short',
        'authentication/tests/',
        'equipment/tests/',
        '--disable-warnings'
    ]) 
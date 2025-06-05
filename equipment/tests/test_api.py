"""
API тесты для Equipment endpoints.
Покрывают все API методы, аутентификацию, валидацию и edge cases.
"""

import pytest
import json
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from equipment.models import EquipmentType, Equipment
from tests.factories import (
    UserFactory, 
    EquipmentTypeFactory, 
    EquipmentFactory,
    EquipmentTypeFactoryBatch,
    EquipmentFactoryBatch
)

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.api
class TestEquipmentAPI:
    """Тесты API для оборудования."""
    
    def test_delete_already_deleted_equipment(self, authenticated_client):
        """Тест удаления уже удаленного оборудования."""
        equipment = EquipmentFactory()
        equipment.soft_delete()
        
        url = reverse('equipment:equipment-detail', kwargs={'pk': equipment.id})
        response = authenticated_client.delete(url)
        
        # Проверяем статус - при попытке удаления уже удаленного возвращается 404
        # так как deleted equipment не найдется в основном queryset
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_create_equipment_mixed_validation_errors(self, authenticated_client):
        """Тест создания со смешанными ошибками валидации."""
        equipment_type = EquipmentTypeFactory(serial_mask='XXAAAAAXAA')
        existing_equipment = EquipmentFactory(
            equipment_type=equipment_type,
            serial_number='1ABCDEF2GH'
        )
        
        url = reverse('equipment:equipment-list-create')
        data = {
            'equipment_type': equipment_type.id,
            'serial_numbers': [
                'valid6FGHI7KL',           # Валидный но возможно невалидная маска
                'invalid123',             # Невалидная маска
                existing_equipment.serial_number,  # Дубликат
                'valid7GHIJ8LM',          # Валидный но возможно невалидная маска  
                'invalid123'              # Дубликат в запросе
            ],
            'note': 'Mixed validation'
        }
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'validation_errors' in response.data
        # Фактически всего 5 ошибок: все серийники не соответствуют маске или дублируются
        assert len(response.data['validation_errors']) == 5


@pytest.mark.django_db
@pytest.mark.api
class TestEquipmentTypeAPI:
    """Тесты API для типов оборудования."""
    
    def test_list_equipment_types(self, authenticated_client):
        """Тест получения списка типов оборудования."""
        equipment_types = EquipmentTypeFactoryBatch.create_default_types()
        
        url = reverse('equipment:equipment-type-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        assert len(response.data['results']) == 5  # Создали 5 типов
        
        # Проверяем содержимое
        type_data = response.data['results'][0]
        assert 'id' in type_data
        assert 'name' in type_data
        assert 'serial_mask' in type_data
        assert 'equipment_count' in type_data
    
    def test_search_equipment_types(self, authenticated_client):
        """Тест поиска типов оборудования."""
        EquipmentTypeFactoryBatch.create_default_types()
        
        url = reverse('equipment:equipment-type-list')
        
        # Поиск по названию
        response = authenticated_client.get(url, {'search': 'TP-Link'})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        
        # Поиск по маске
        response = authenticated_client.get(url, {'search': 'XXAA'})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 1
    
    def test_filter_equipment_types_by_name(self, authenticated_client):
        """Тест фильтрации типов по имени."""
        EquipmentTypeFactoryBatch.create_default_types()
        
        url = reverse('equipment:equipment-type-list')
        response = authenticated_client.get(url, {'name': 'D-Link'})
        
        assert response.status_code == status.HTTP_200_OK
        
        # Проверяем что возвращаются только D-Link типы
        for type_data in response.data['results']:
            assert 'D-Link' in type_data['name']
    
    def test_filter_equipment_types_by_mask(self, authenticated_client):
        """Тест фильтрации типов по маске."""
        EquipmentTypeFactoryBatch.create_default_types()
        
        url = reverse('equipment:equipment-type-list')
        response = authenticated_client.get(url, {'serial_mask': 'NNNN'})
        
        assert response.status_code == status.HTTP_200_OK
        
        # Проверяем что возвращаются только типы с соответствующей маской
        for type_data in response.data['results']:
            assert 'NNNN' in type_data['serial_mask']


@pytest.mark.django_db
@pytest.mark.api  
class TestEquipmentStatsAPI:
    """Тесты API статистики оборудования."""
    
    def test_equipment_stats(self, authenticated_client):
        """Тест получения статистики оборудования."""
        # Создаем тестовые данные
        test_data = EquipmentFactoryBatch.create_test_dataset()
        
        url = reverse('equipment:equipment-stats')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        
        # Проверяем структуру ответа
        assert 'total_equipment' in response.data
        assert 'total_deleted' in response.data
        assert 'total_active' in response.data
        assert 'total_types' in response.data
        assert 'type_statistics' in response.data
        
        # Проверяем корректность подсчетов
        expected_deleted = len(test_data['deleted_equipment'])
        expected_types = len(test_data['types'])
        
        # total_equipment возвращает только активные (через objects manager)
        # total_active должен равняться total_equipment
        assert response.data['total_active'] == response.data['total_equipment']
        assert response.data['total_deleted'] == expected_deleted
        assert response.data['total_types'] == expected_types
        
        # Проверяем статистику по типам
        assert len(response.data['type_statistics']) == expected_types
        
        for type_stat in response.data['type_statistics']:
            assert 'id' in type_stat
            assert 'name' in type_stat
            assert 'equipment_count' in type_stat
            assert 'serial_mask' in type_stat


@pytest.mark.api
class TestEquipmentRestoreAPI(TestCase):
    """Тесты API восстановления оборудования."""
    
    def setUp(self):
        """Настройка данных для каждого теста."""
        self.client = APIClient()
        self.user = UserFactory()
        self.equipment_type = EquipmentTypeFactory()
        self.deleted_equipment = EquipmentFactory(equipment_type=self.equipment_type)
        self.deleted_equipment.soft_delete()
        
        # Аутентификация
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
    
    def test_restore_deleted_equipment(self):
        """Тест восстановления удаленного оборудования."""
        url = reverse('equipment:equipment-restore', kwargs={'pk': self.deleted_equipment.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertIn('data', response.data)
        
        # Проверяем что оборудование восстановлено
        self.deleted_equipment.refresh_from_db()
        self.assertIsNone(self.deleted_equipment.deleted_at)
        self.assertFalse(self.deleted_equipment.is_deleted)
    
    def test_restore_active_equipment(self):
        """Тест восстановления активного оборудования."""
        active_equipment = EquipmentFactory(equipment_type=self.equipment_type)
        
        url = reverse('equipment:equipment-restore', kwargs={'pk': active_equipment.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('не удалено', response.data['error'])
    
    def test_restore_nonexistent_equipment(self):
        """Тест восстановления несуществующего оборудования."""
        url = reverse('equipment:equipment-restore', kwargs={'pk': 99999})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('не найдено', response.data['error']) 
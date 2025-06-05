"""
Unit тесты для сериализаторов Equipment.
Покрывают валидацию, DTO pattern и бизнес-логику.
"""

import pytest
from django.test import TestCase
from rest_framework.exceptions import ValidationError

from equipment.models import EquipmentType, Equipment
from equipment.serializers import (
    EquipmentTypeSerializer,
    EquipmentSerializer,
    EquipmentCreateSerializer,
    EquipmentUpdateSerializer
)
from tests.factories import EquipmentTypeFactory, EquipmentFactory


@pytest.mark.serializer
class TestEquipmentTypeSerializer(TestCase):
    """Тесты для EquipmentTypeSerializer."""
    
    def setUp(self):
        """Настройка данных для каждого теста."""
        self.equipment_type = EquipmentTypeFactory(
            name='Test Router',
            serial_mask='XXAAAAAXAA'
        )
        # Создаем оборудование для подсчета
        EquipmentFactory.create_batch(3, equipment_type=self.equipment_type)
    
    def test_serialization(self):
        """Тест сериализации типа оборудования."""
        serializer = EquipmentTypeSerializer(self.equipment_type)
        data = serializer.data
        
        self.assertEqual(data['id'], self.equipment_type.id)
        self.assertEqual(data['name'], self.equipment_type.name)
        self.assertEqual(data['serial_mask'], self.equipment_type.serial_mask)
        self.assertEqual(data['equipment_count'], 3)
        self.assertIn('created_at', data)
        self.assertIn('updated_at', data)
    
    def test_equipment_count_calculation(self):
        """Тест корректного подсчета количества оборудования."""
        # Создаем дополнительное оборудование
        EquipmentFactory.create_batch(2, equipment_type=self.equipment_type)
        
        serializer = EquipmentTypeSerializer(self.equipment_type)
        self.assertEqual(serializer.data['equipment_count'], 5)
    
    def test_equipment_count_excludes_deleted(self):
        """Тест что подсчет исключает удаленное оборудование."""
        # Удаляем одну единицу оборудования
        equipment = Equipment.objects.filter(equipment_type=self.equipment_type).first()
        equipment.soft_delete()
        
        serializer = EquipmentTypeSerializer(self.equipment_type)
        self.assertEqual(serializer.data['equipment_count'], 2)  # 3 - 1 удаленная
    
    def test_multiple_types_serialization(self):
        """Тест сериализации нескольких типов."""
        types = EquipmentTypeFactory.create_batch(3)
        serializer = EquipmentTypeSerializer(types, many=True)
        
        self.assertEqual(len(serializer.data), 3)
        for type_data in serializer.data:
            self.assertIn('id', type_data)
            self.assertIn('name', type_data)
            self.assertIn('equipment_count', type_data)


@pytest.mark.serializer
class TestEquipmentSerializer(TestCase):
    """Тесты для EquipmentSerializer."""
    
    def setUp(self):
        """Настройка данных для каждого теста."""
        self.equipment_type = EquipmentTypeFactory(
            name='Test Router',
            serial_mask='XXAAAAAXAA'
        )
        self.equipment = EquipmentFactory(
            equipment_type=self.equipment_type,
            serial_number='1ABCDEF2GH',
            note='Test equipment'
        )
    
    def test_serialization(self):
        """Тест сериализации оборудования."""
        serializer = EquipmentSerializer(self.equipment)
        data = serializer.data
        
        self.assertEqual(data['id'], self.equipment.id)
        self.assertEqual(data['equipment_type'], self.equipment_type.id)
        self.assertEqual(data['equipment_type_name'], self.equipment_type.name)
        self.assertEqual(data['equipment_type_mask'], self.equipment_type.serial_mask)
        self.assertEqual(data['serial_number'], self.equipment.serial_number)
        self.assertEqual(data['note'], self.equipment.note)
        self.assertIn('created_at', data)
        self.assertIn('updated_at', data)
    
    def test_validation_valid_serial(self):
        """Тест валидации корректного серийного номера."""
        data = {
            'equipment_type': self.equipment_type.id,
            'serial_number': '9ZYXWVU8KL',
            'note': 'Valid equipment'
        }
        
        serializer = EquipmentSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        validated_data = serializer.validated_data
        self.assertEqual(validated_data['equipment_type'], self.equipment_type)
        self.assertEqual(validated_data['serial_number'], '9ZYXWVU8KL')
    
    def test_validation_invalid_serial_mask(self):
        """Тест валидации некорректного серийного номера по маске."""
        data = {
            'equipment_type': self.equipment_type.id,
            'serial_number': 'invalid123',  # Не соответствует маске XXAAAAAXAA
            'note': 'Invalid equipment'
        }
        
        serializer = EquipmentSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('serial_number', serializer.errors)
        self.assertIn('не соответствует маске', str(serializer.errors['serial_number'][0]))
    
    def test_validation_duplicate_serial_create(self):
        """Тест валидации дублирующегося серийного номера при создании."""
        data = {
            'equipment_type': self.equipment_type.id,
            'serial_number': self.equipment.serial_number,  # Уже существует
            'note': 'Duplicate equipment'
        }
        
        serializer = EquipmentSerializer(data=data)
        assert not serializer.is_valid()
        # Ошибка может быть в serial_number или non_field_errors
        assert 'serial_number' in serializer.errors or 'non_field_errors' in serializer.errors
        if 'serial_number' in serializer.errors:
            assert 'уже существует' in str(serializer.errors['serial_number'][0])
        else:
            # Django стандартная ошибка unique_together
            assert 'уникальными значениями' in str(serializer.errors['non_field_errors'][0])
    
    def test_validation_duplicate_serial_update_same_object(self):
        """Тест что при обновлении объект может оставить свой серийник."""
        data = {
            'equipment_type': self.equipment_type.id,
            'serial_number': self.equipment.serial_number,  # Тот же серийник
            'note': 'Updated note'
        }
        
        serializer = EquipmentSerializer(self.equipment, data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_validation_duplicate_serial_update_different_object(self):
        """Тест валидации дублирующегося серийника при обновлении другого объекта."""
        other_equipment = EquipmentFactory(
            equipment_type=self.equipment_type,
            serial_number='8HIJKLM9NO'
        )
        
        data = {
            'equipment_type': self.equipment_type.id,
            'serial_number': self.equipment.serial_number,  # Серийник первого объекта
            'note': 'Updated equipment'
        }
        
        serializer = EquipmentSerializer(other_equipment, data=data)
        assert not serializer.is_valid()
        # Ошибка может быть в serial_number или non_field_errors
        assert 'serial_number' in serializer.errors or 'non_field_errors' in serializer.errors
        if 'serial_number' in serializer.errors:
            assert 'уже существует' in str(serializer.errors['serial_number'][0])
        else:
            # Django стандартная ошибка unique_together
            assert 'уникальными значениями' in str(serializer.errors['non_field_errors'][0])
    
    def test_validation_change_equipment_type(self):
        """Тест изменения типа оборудования с валидацией серийника."""
        # Создаем новый тип с другой маской
        new_type = EquipmentTypeFactory(serial_mask='NNNNAAAA')
        
        data = {
            'equipment_type': new_type.id,
            'serial_number': '1234ABCD',  # Соответствует новой маске
            'note': 'Changed type'
        }
        
        serializer = EquipmentSerializer(self.equipment, data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_validation_change_type_invalid_serial(self):
        """Тест изменения типа с серийником, не подходящим к новой маске."""
        new_type = EquipmentTypeFactory(serial_mask='NNNNAAAA')
        
        data = {
            'equipment_type': new_type.id,
            'serial_number': self.equipment.serial_number,  # Не подходит к новой маске
            'note': 'Invalid type change'
        }
        
        serializer = EquipmentSerializer(self.equipment, data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('serial_number', serializer.errors)


@pytest.mark.serializer
class TestEquipmentCreateSerializer(TestCase):
    """Тесты для EquipmentCreateSerializer."""
    
    def setUp(self):
        """Настройка данных для каждого теста."""
        self.equipment_type = EquipmentTypeFactory(
            name='Test Router',
            serial_mask='XXAAAAAXAA'
        )
    
    def test_valid_single_serial(self):
        """Тест валидации одного серийного номера."""
        data = {
            'equipment_type': self.equipment_type.id,
            'serial_numbers': ['1ABCDEF2GH'],
            'note': 'Single equipment'
        }
        
        serializer = EquipmentCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        validated_data = serializer.validated_data
        self.assertEqual(len(validated_data['valid_serial_numbers']), 1)
        self.assertEqual(validated_data['valid_serial_numbers'][0], '1ABCDEF2GH')
    
    def test_valid_multiple_serials(self):
        """Тест валидации нескольких серийных номеров."""
        data = {
            'equipment_type': self.equipment_type.id,
            'serial_numbers': ['1ABCDEF2GH', '3CDEFGH4IJ', '5EFGHIJ6KL'],
            'note': 'Multiple equipment'
        }
        
        serializer = EquipmentCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        validated_data = serializer.validated_data
        self.assertEqual(len(validated_data['valid_serial_numbers']), 3)
    
    def test_invalid_serial_mask(self):
        """Тест валидации с невалидными серийными номерами по маске."""
        data = {
            'equipment_type': self.equipment_type.id,
            'serial_numbers': ['invalid123', 'alsoinvalid'],
            'note': 'Invalid equipment'
        }
        
        serializer = EquipmentCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('validation_errors', serializer.errors)
        
        errors = serializer.errors['validation_errors']
        self.assertEqual(len(errors), 2)
        
        for error in errors:
            self.assertIn('serial_number', error)
            self.assertIn('errors', error)
            self.assertIn('не соответствует маске', error['errors'][0])
    
    def test_duplicate_serials_in_db(self):
        """Тест валидации с серийниками, уже существующими в БД."""
        # Создаем существующее оборудование
        existing = EquipmentFactory(
            equipment_type=self.equipment_type,
            serial_number='1ABCDEF2GH'
        )
        
        data = {
            'equipment_type': self.equipment_type.id,
            'serial_numbers': ['1ABCDEF2GH'],  # Уже существует
            'note': 'Duplicate equipment'
        }
        
        serializer = EquipmentCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        
        errors = serializer.errors['validation_errors']
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]['serial_number'], '1ABCDEF2GH')
        self.assertIn('уже существует в базе данных', errors[0]['errors'][0])
    
    def test_duplicate_serials_in_request(self):
        """Тест валидации с дубликатами в одном запросе."""
        data = {
            'equipment_type': self.equipment_type.id,
            'serial_numbers': ['1ABCDEF2GH', '1ABCDEF2GH'],  # Дубликат
            'note': 'Duplicate in request'
        }
        
        serializer = EquipmentCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        
        errors = serializer.errors['validation_errors']
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]['serial_number'], '1ABCDEF2GH')
        self.assertIn('дублируется в текущем запросе', errors[0]['errors'][0])
    
    def test_mixed_validation_errors(self):
        """Тест со смешанными ошибками валидации."""
        # Создаем существующее оборудование
        EquipmentFactory(
            equipment_type=self.equipment_type,
            serial_number='1ABCDEF2GH'
        )
        
        data = {
            'equipment_type': self.equipment_type.id,
            'serial_numbers': [
                '1ABCDEF2GH',     # Существует в БД
                'invalid123',     # Невалидная маска
                '3CDEFGH4IJ',     # Валидный
                '3CDEFGH4IJ',     # Дубликат в запросе
                'alsoinvalid'     # Невалидная маска
            ],
            'note': 'Mixed errors'
        }
        
        serializer = EquipmentCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        
        errors = serializer.errors['validation_errors']
        self.assertEqual(len(errors), 4)  # 4 ошибки из 5 серийников
    
    def test_empty_serial_numbers(self):
        """Тест валидации пустого списка серийных номеров."""
        data = {
            'equipment_type': self.equipment_type.id,
            'serial_numbers': [],
            'note': 'Empty list'
        }
        
        serializer = EquipmentCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('serial_numbers', serializer.errors)
    
    def test_create_equipment(self):
        """Тест создания оборудования через сериализатор."""
        data = {
            'equipment_type': self.equipment_type.id,
            'serial_numbers': ['1ABCDEF2GH', '3CDEFGH4IJ'],
            'note': 'Created equipment'
        }
        
        serializer = EquipmentCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        # Создаем оборудование
        created_equipment = serializer.save()
        
        self.assertEqual(len(created_equipment), 2)
        
        # Проверяем что оборудование создано в БД
        equipment1 = Equipment.objects.get(serial_number='1ABCDEF2GH')
        equipment2 = Equipment.objects.get(serial_number='3CDEFGH4IJ')
        
        self.assertEqual(equipment1.equipment_type, self.equipment_type)
        self.assertEqual(equipment1.note, 'Created equipment')
        self.assertEqual(equipment2.equipment_type, self.equipment_type)
        self.assertEqual(equipment2.note, 'Created equipment')


@pytest.mark.serializer
class TestEquipmentUpdateSerializer(TestCase):
    """Тесты для EquipmentUpdateSerializer."""
    
    def setUp(self):
        """Настройка данных для каждого теста."""
        self.equipment_type = EquipmentTypeFactory(
            name='Test Router',
            serial_mask='XXAAAAAXAA'
        )
        self.equipment = EquipmentFactory(
            equipment_type=self.equipment_type,
            serial_number='1ABCDEF2GH',
            note='Original note'
        )
    
    def test_valid_update(self):
        """Тест валидного обновления."""
        data = {
            'equipment_type': self.equipment_type.id,
            'serial_number': '9ZYXWVU8KL',
            'note': 'Updated note'
        }
        
        serializer = EquipmentUpdateSerializer(self.equipment, data=data)
        self.assertTrue(serializer.is_valid())
        
        # Выполняем обновление
        updated_equipment = serializer.save()
        
        self.assertEqual(updated_equipment.serial_number, '9ZYXWVU8KL')
        self.assertEqual(updated_equipment.note, 'Updated note')
    
    def test_partial_update(self):
        """Тест частичного обновления."""
        data = {'note': 'Partially updated note'}
        
        serializer = EquipmentUpdateSerializer(
            self.equipment, 
            data=data, 
            partial=True
        )
        self.assertTrue(serializer.is_valid())
        
        updated_equipment = serializer.save()
        
        # Серийный номер не изменился
        self.assertEqual(updated_equipment.serial_number, '1ABCDEF2GH')
        # Примечание изменилось
        self.assertEqual(updated_equipment.note, 'Partially updated note')
    
    def test_inheritance_from_equipment_serializer(self):
        """Тест что UpdateSerializer наследует валидацию от EquipmentSerializer."""
        data = {
            'equipment_type': self.equipment_type.id,
            'serial_number': 'invalid123',  # Невалидная маска
            'note': 'Invalid update'
        }
        
        serializer = EquipmentUpdateSerializer(self.equipment, data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('serial_number', serializer.errors)
        self.assertIn('не соответствует маске', str(serializer.errors['serial_number'][0])) 
"""
Unit тесты для моделей Equipment.
Покрывают все методы, валидацию и бизнес-логику.
"""

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone
from freezegun import freeze_time

from equipment.models import EquipmentType, Equipment
from tests.factories import EquipmentTypeFactory, EquipmentFactory, UserFactory


@pytest.mark.django_db
@pytest.mark.model
class TestEquipmentType:
    """Тесты для модели EquipmentType."""
    
    def test_str_representation(self):
        """Тест строкового представления модели."""
        equipment_type = EquipmentTypeFactory(name='Test Router')
        assert str(equipment_type) == 'Test Router'
    
    def test_get_regex_pattern_digits(self):
        """Тест преобразования маски с цифрами."""
        equipment_type = EquipmentTypeFactory(serial_mask='NNN')
        pattern = equipment_type.get_regex_pattern()
        assert pattern == '^[0-9][0-9][0-9]$'
    
    def test_get_regex_pattern_uppercase(self):
        """Тест преобразования маски с заглавными буквами."""
        equipment_type = EquipmentTypeFactory(serial_mask='AAA')
        pattern = equipment_type.get_regex_pattern()
        assert pattern == '^[A-Z][A-Z][A-Z]$'
    
    def test_get_regex_pattern_lowercase(self):
        """Тест преобразования маски со строчными буквами."""
        equipment_type = EquipmentTypeFactory(serial_mask='aaa')
        pattern = equipment_type.get_regex_pattern()
        assert pattern == '^[a-z][a-z][a-z]$'
    
    def test_get_regex_pattern_alphanumeric(self):
        """Тест преобразования маски с буквами и цифрами."""
        equipment_type = EquipmentTypeFactory(serial_mask='XXX')
        pattern = equipment_type.get_regex_pattern()
        assert pattern == '^[A-Z0-9][A-Z0-9][A-Z0-9]$'
    
    def test_get_regex_pattern_special_chars(self):
        """Тест преобразования маски со спецсимволами."""
        equipment_type = EquipmentTypeFactory(serial_mask='ZZZ')
        pattern = equipment_type.get_regex_pattern()
        assert pattern == '^[-_@][-_@][-_@]$'
    
    def test_get_regex_pattern_mixed(self):
        """Тест преобразования сложной маски."""
        equipment_type = EquipmentTypeFactory(serial_mask='NXAaZ')
        pattern = equipment_type.get_regex_pattern()
        assert pattern == '^[0-9][A-Z0-9][A-Z][a-z][-_@]$'
    
    def test_get_regex_pattern_literal_chars(self):
        """Тест экранирования литеральных символов."""
        equipment_type = EquipmentTypeFactory(serial_mask='AA-BB.CC')
        pattern = equipment_type.get_regex_pattern()
        assert pattern == '^[A-Z][A-Z]\\-BB\\.CC$'
    
    def test_validate_serial_number_valid(self):
        """Тест валидации корректного серийного номера."""
        equipment_type = EquipmentTypeFactory(serial_mask='XXAAAAAXAA')
        valid_serials = [
            '1ABCDEF2GH',
            'AABCDEF1IJ',
            '9ZYXWVU8KL'
        ]
        
        for serial in valid_serials:
            assert equipment_type.validate_serial_number(serial)
    
    def test_validate_serial_number_invalid(self):
        """Тест валидации некорректного серийного номера."""
        equipment_type = EquipmentTypeFactory(serial_mask='XXAAAAAXAA')
        invalid_serials = [
            'aaBCDEF2GH',  # строчные вместо заглавных/цифр
            '1ABCDEF2g',   # строчная в конце
            '1ABCDEF2',    # короткий
            '1ABCDEF2GHI', # длинный
            '1abcdef2GH',  # строчные вместо заглавных
        ]
        
        for serial in invalid_serials:
            assert not equipment_type.validate_serial_number(serial)
    
    def test_validate_serial_number_with_special_chars(self):
        """Тест валидации серийного номера со спецсимволами."""
        equipment_type = EquipmentTypeFactory(serial_mask='AAZAA')
        
        valid_serials = ['AA-AA', 'AA_AA', 'AA@AA']
        invalid_serials = ['AA#AA', 'AA*AA', 'AA AA']
        
        for serial in valid_serials:
            assert equipment_type.validate_serial_number(serial)
        
        for serial in invalid_serials:
            assert not equipment_type.validate_serial_number(serial)
    
    def test_name_max_length(self):
        """Тест максимальной длины названия."""
        long_name = 'x' * 256  # Превышаем лимит в 255 символов
        with pytest.raises(ValidationError):
            equipment_type = EquipmentType(name=long_name, serial_mask='AAA')
            equipment_type.full_clean()
    
    def test_serial_mask_max_length(self):
        """Тест максимальной длины маски."""
        long_mask = 'A' * 51  # Превышаем лимит в 50 символов
        with pytest.raises(ValidationError):
            equipment_type = EquipmentType(name='Test', serial_mask=long_mask)
            equipment_type.full_clean()
    
    def test_timestamps_auto_generation(self):
        """Тест автоматической генерации временных меток."""
        with freeze_time("2023-01-01 12:00:00"):
            equipment_type = EquipmentTypeFactory()
            assert equipment_type.created_at.strftime("%Y-%m-%d %H:%M:%S") == "2023-01-01 12:00:00"
            assert equipment_type.updated_at.strftime("%Y-%m-%d %H:%M:%S") == "2023-01-01 12:00:00"


@pytest.mark.django_db
@pytest.mark.model
class TestEquipment:
    """Тесты для модели Equipment."""
    
    def test_str_representation(self):
        """Тест строкового представления модели."""
        equipment_type = EquipmentTypeFactory(name='Test Router')
        equipment = EquipmentFactory(
            equipment_type=equipment_type,
            serial_number='1ABCDEF2GH'
        )
        expected = f"{equipment_type.name} - {equipment.serial_number}"
        assert str(equipment) == expected
    
    def test_unique_together_constraint(self):
        """Тест уникальности комбинации тип+серийный номер."""
        equipment_type = EquipmentTypeFactory()
        EquipmentFactory(equipment_type=equipment_type, serial_number='TEST123')
        
        with pytest.raises(IntegrityError):
            Equipment.objects.create(
                equipment_type=equipment_type,
                serial_number='TEST123',
                note='Duplicate equipment'
            )
    
    def test_soft_delete(self):
        """Тест мягкого удаления."""
        equipment = EquipmentFactory()
        assert equipment.deleted_at is None
        assert not equipment.is_deleted
        
        with freeze_time("2023-01-01 12:00:00"):
            equipment.soft_delete()
        
        assert equipment.deleted_at is not None
        assert equipment.is_deleted
        assert equipment.deleted_at.strftime("%Y-%m-%d %H:%M:%S") == "2023-01-01 12:00:00"
    
    def test_restore(self):
        """Тест восстановления удаленной записи."""
        equipment = EquipmentFactory()
        equipment.soft_delete()
        assert equipment.is_deleted
        
        equipment.restore()
        assert equipment.deleted_at is None
        assert not equipment.is_deleted
    
    def test_is_deleted_property(self):
        """Тест свойства is_deleted."""
        equipment = EquipmentFactory()
        assert not equipment.is_deleted
        
        equipment.soft_delete()
        assert equipment.is_deleted
    
    def test_manager_excludes_deleted(self):
        """Тест что обычный менеджер исключает удаленные."""
        equipment = EquipmentFactory()
        equipment.soft_delete()
        
        # Обычный менеджер не должен возвращать удаленные
        assert not Equipment.objects.filter(id=equipment.id).exists()
    
    def test_manager_deleted_only(self):
        """Тест менеджера только удаленных."""
        equipment = EquipmentFactory()
        equipment.soft_delete()
        
        # Менеджер удаленных должен возвращать только удаленные
        assert Equipment.deleted_objects.filter(id=equipment.id).exists()
    
    def test_manager_with_deleted(self):
        """Тест менеджера с удаленными."""
        equipment = EquipmentFactory()
        equipment.soft_delete()
        
        # Менеджер всех должен возвращать все записи
        assert Equipment.all_objects.filter(id=equipment.id).exists()
    
    def test_serial_number_max_length(self):
        """Тест максимальной длины серийного номера."""
        long_serial = 'x' * 101  # Превышаем лимит в 100 символов
        with pytest.raises(ValidationError):
            equipment = Equipment(
                equipment_type=EquipmentTypeFactory(),
                serial_number=long_serial
            )
            equipment.full_clean()
    
    def test_note_optional(self):
        """Тест что заметка опциональна."""
        equipment = EquipmentFactory(note='')
        equipment.full_clean()  # Не должно вызывать ошибку
        assert equipment.note == ''
    
    def test_note_can_be_blank(self):
        """Тест что заметка может быть пустой."""
        equipment = EquipmentFactory()
        equipment.note = ''
        equipment.save()
        equipment.refresh_from_db()
        assert equipment.note == ''
    
    def test_equipment_type_cascade_delete(self):
        """Тест каскадного удаления при удалении типа."""
        equipment_type = EquipmentTypeFactory()
        equipment = EquipmentFactory(equipment_type=equipment_type)
        
        equipment_type.delete()
        assert not Equipment.objects.filter(id=equipment.id).exists()
    
    def test_ordering(self):
        """Тест сортировки по умолчанию."""
        equipment1 = EquipmentFactory()
        equipment2 = EquipmentFactory()
        
        # Должны быть отсортированы по created_at в убывающем порядке
        equipments = list(Equipment.objects.all())
        assert equipments[0].created_at >= equipments[1].created_at
    
    def test_timestamps_auto_generation(self):
        """Тест автоматической генерации временных меток."""
        with freeze_time("2023-01-01 12:00:00"):
            equipment = EquipmentFactory()
            assert equipment.created_at.strftime("%Y-%m-%d %H:%M:%S") == "2023-01-01 12:00:00"
            assert equipment.updated_at.strftime("%Y-%m-%d %H:%M:%S") == "2023-01-01 12:00:00"
    
    def test_updated_at_changes_on_save(self):
        """Тест что updated_at обновляется при сохранении."""
        with freeze_time("2023-01-01 12:00:00"):
            equipment = EquipmentFactory()
            original_updated_at = equipment.updated_at
        
        with freeze_time("2023-01-02 12:00:00"):
            equipment.note = "Updated note"
            equipment.save()
            
        assert equipment.updated_at > original_updated_at
        assert equipment.updated_at.strftime("%Y-%m-%d %H:%M:%S") == "2023-01-02 12:00:00" 
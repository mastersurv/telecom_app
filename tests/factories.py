"""
Фабрики для создания тестовых данных.
Используют library factory_boy для генерации объектов.
"""

import factory
import random
import string
from django.contrib.auth import get_user_model

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    """Фабрика для создания пользователей."""
    
    class Meta:
        model = User
        skip_postgeneration_save = True
    
    username = factory.Sequence(lambda n: f"testuser{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    is_active = True
    is_staff = False
    is_superuser = False
    
    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        if not create:
            return
        
        password = extracted or 'testpassword123'
        self.set_password(password)
        self.save()


class SuperUserFactory(UserFactory):
    """Фабрика для создания суперпользователей."""
    
    is_staff = True
    is_superuser = True
    username = factory.Sequence(lambda n: f"admin{n}")


class EquipmentTypeFactory(factory.django.DjangoModelFactory):
    """Фабрика для создания типов оборудования."""
    
    class Meta:
        model = 'equipment.EquipmentType'
    
    name = factory.Iterator([
        'TP-Link TL-WR74',
        'D-Link DIR-300',
        'D-Link DIR-300 E',
        'Cisco ISR4000',
        'Huawei AR6300',
        'MikroTik hEX',
        'Ubiquiti EdgeRouter',
        'ZyXEL Keenetic',
        'ASUS RT-AX6000',
        'NetGear Nighthawk'
    ])
    
    serial_mask = factory.Iterator([
        'XXAAAAAXAA',
        'NXXAAXZXaa', 
        'NAAAAXZXXX',
        'NNNNAAAA',
        'XXXX-AAAA',
        'NNA_AAA',
        'XX@AAANN',
        'AANNAAZZX',
        'NNNXAAAXXX',
        'AAXXNNZZAA'
    ])


def generate_valid_serial_for_mask(mask):
    """Генерирует валидный серийный номер согласно маске."""
    serial = ""
    
    for char in mask:
        if char == 'N':
            serial += random.choice(string.digits)
        elif char == 'A':
            serial += random.choice(string.ascii_uppercase)
        elif char == 'a':
            serial += random.choice(string.ascii_lowercase)
        elif char == 'X':
            serial += random.choice(string.ascii_uppercase + string.digits)
        elif char == 'Z':
            serial += random.choice('-_@')
        else:
            serial += char
    
    return serial


class EquipmentFactory(factory.django.DjangoModelFactory):
    """Фабрика для создания оборудования."""
    
    class Meta:
        model = 'equipment.Equipment'
    
    equipment_type = factory.SubFactory(EquipmentTypeFactory)
    serial_number = factory.LazyAttribute(
        lambda obj: generate_valid_serial_for_mask(obj.equipment_type.serial_mask)
    )
    note = factory.Faker('text', max_nb_chars=200)
    deleted_at = None


class DeletedEquipmentFactory(EquipmentFactory):
    """Фабрика для создания удаленного оборудования."""
    
    deleted_at = factory.Faker('date_time_this_year')


# Batch фабрики для массового создания
class EquipmentTypeFactoryBatch:
    """Утилиты для массового создания типов оборудования."""
    
    @staticmethod
    def create_default_types():
        """Создает стандартный набор типов оборудования."""
        from equipment.models import EquipmentType
        
        types_data = [
            {'name': 'TP-Link TL-WR74', 'serial_mask': 'XXAAAAAXAA'},
            {'name': 'D-Link DIR-300', 'serial_mask': 'NXXAAXZXaa'},
            {'name': 'D-Link DIR-300 E', 'serial_mask': 'NAAAAXZXXX'},
            {'name': 'Cisco ISR4000', 'serial_mask': 'NNNNAAAA'},
            {'name': 'Huawei AR6300', 'serial_mask': 'XXXX-AAAA'},
        ]
        
        created_types = []
        for data in types_data:
            equipment_type, created = EquipmentType.objects.get_or_create(**data)
            created_types.append(equipment_type)
        
        return created_types


class EquipmentFactoryBatch:
    """Утилиты для массового создания оборудования."""
    
    @staticmethod
    def create_multiple_for_type(equipment_type, count=5):
        """Создает несколько единиц оборудования для конкретного типа."""
        equipment_list = []
        
        for i in range(count):
            equipment = EquipmentFactory(equipment_type=equipment_type)
            equipment_list.append(equipment)
        
        return equipment_list
    
    @staticmethod
    def create_test_dataset():
        """Создает полный тестовый набор данных."""
        # Создаем типы оборудования
        types = EquipmentTypeFactoryBatch.create_default_types()
        
        # Создаем оборудование для каждого типа
        all_equipment = []
        for equipment_type in types:
            equipment_list = EquipmentFactoryBatch.create_multiple_for_type(
                equipment_type, count=3
            )
            all_equipment.extend(equipment_list)
        
        # Создаем несколько удаленных записей
        deleted_equipment = [
            DeletedEquipmentFactory(equipment_type=types[0]),
            DeletedEquipmentFactory(equipment_type=types[1]),
        ]
        all_equipment.extend(deleted_equipment)
        
        return {
            'types': types,
            'equipment': all_equipment,
            'active_equipment': [eq for eq in all_equipment if not eq.deleted_at],
            'deleted_equipment': [eq for eq in all_equipment if eq.deleted_at],
        } 
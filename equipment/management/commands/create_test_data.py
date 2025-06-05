from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from equipment.models import EquipmentType, Equipment


class Command(BaseCommand):
    """
    Команда для создания тестовых данных.
    
    Создает типы оборудования из технического задания и несколько примеров оборудования.
    """
    
    help = 'Создает тестовые данные для приложения'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Очистить существующие данные перед созданием новых',
        )
    
    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Очистка существующих данных...')
            Equipment.all_objects.all().delete()
            EquipmentType.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Данные очищены'))
        
        # Создаем типы оборудования из технического задания
        equipment_types_data = [
            {'name': 'TP-Link TL-WR74', 'serial_mask': 'XXAAAAAXAA'},
            {'name': 'D-Link DIR-300', 'serial_mask': 'NXXAAXZXaa'},
            {'name': 'D-Link DIR-300 E', 'serial_mask': 'NAAAAXZXXX'},
        ]
        
        self.stdout.write('Создание типов оборудования...')
        
        for type_data in equipment_types_data:
            equipment_type, created = EquipmentType.objects.get_or_create(
                name=type_data['name'],
                defaults={'serial_mask': type_data['serial_mask']}
            )
            
            if created:
                self.stdout.write(f'  Создан тип: {equipment_type.name}')
            else:
                self.stdout.write(f'  Тип уже существует: {equipment_type.name}')
        
        # Создаем примеры оборудования
        self.stdout.write('Создание примеров оборудования...')
        
        equipment_examples = [
            {
                'type_name': 'TP-Link TL-WR74',
                'serial_numbers': ['12ABCDEF34', 'AB12345CDE', '99ZXYWAB12'],
                'note': 'Тестовое оборудование TP-Link'
            },
            {
                'type_name': 'D-Link DIR-300',
                'serial_numbers': ['123AB4_DEf', '987CD2@HIj', '456EF1-KLm'],
                'note': 'Тестовое оборудование D-Link DIR-300'
            },
            {
                'type_name': 'D-Link DIR-300 E',
                'serial_numbers': ['1ABCD2@ABC', '5EFGH9_XYZ', '7IJKL3-MNO'],
                'note': 'Тестовое оборудование D-Link DIR-300 E'
            },
        ]
        
        for example in equipment_examples:
            try:
                equipment_type = EquipmentType.objects.get(name=example['type_name'])
                
                for serial_number in example['serial_numbers']:
                    # Проверяем валидность серийного номера
                    if not equipment_type.validate_serial_number(serial_number):
                        self.stdout.write(
                            self.style.WARNING(
                                f'  Серийный номер {serial_number} не соответствует маске {equipment_type.serial_mask}'
                            )
                        )
                        continue
                    
                    equipment, created = Equipment.objects.get_or_create(
                        equipment_type=equipment_type,
                        serial_number=serial_number,
                        defaults={'note': example['note']}
                    )
                    
                    if created:
                        self.stdout.write(f'  Создано оборудование: {equipment}')
                    else:
                        self.stdout.write(f'  Оборудование уже существует: {equipment}')
                        
            except EquipmentType.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Тип оборудования {example["type_name"]} не найден')
                )
        
        # Создаем суперпользователя для тестирования
        self.stdout.write('Создание тестового пользователя...')
        
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123'
            )
            self.stdout.write('  Создан суперпользователь: admin/admin123')
        else:
            self.stdout.write('  Суперпользователь уже существует')
        
        if not User.objects.filter(username='testuser').exists():
            User.objects.create_user(
                username='testuser',
                email='test@example.com',
                password='test123'
            )
            self.stdout.write('  Создан тестовый пользователь: testuser/test123')
        else:
            self.stdout.write('  Тестовый пользователь уже существует')
        
        self.stdout.write(self.style.SUCCESS('Тестовые данные успешно созданы!')) 
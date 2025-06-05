from rest_framework import serializers
from django.db import transaction
from .models import Equipment, EquipmentType


class EquipmentTypeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для типа оборудования.
    
    Используется для вывода списка типов оборудования и работы с отдельными типами.
    """
    
    equipment_count = serializers.SerializerMethodField()
    
    class Meta:
        model = EquipmentType
        fields = [
            'id',
            'name', 
            'serial_mask',
            'equipment_count',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'equipment_count']
    
    def get_equipment_count(self, obj) -> int:
        """
        Возвращает количество единиц оборудования данного типа.
        """
        return obj.equipment.count()


class EquipmentSerializer(serializers.ModelSerializer):
    """
    Сериализатор для оборудования.
    
    Используется для отображения данных об оборудовании.
    """
    
    equipment_type_name = serializers.CharField(
        source='equipment_type.name', 
        read_only=True
    )
    equipment_type_mask = serializers.CharField(
        source='equipment_type.serial_mask',
        read_only=True
    )
    
    class Meta:
        model = Equipment
        fields = [
            'id',
            'equipment_type',
            'equipment_type_name',
            'equipment_type_mask',
            'serial_number',
            'note',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id', 
            'created_at', 
            'updated_at',
            'equipment_type_name',
            'equipment_type_mask'
        ]
    
    def validate(self, attrs):
        """
        Валидирует данные оборудования.
        """
        equipment_type = attrs.get('equipment_type')
        serial_number = attrs.get('serial_number')
        
        if equipment_type and serial_number:
            if not equipment_type.validate_serial_number(serial_number):
                raise serializers.ValidationError({
                    'serial_number': f'Серийный номер не соответствует маске {equipment_type.serial_mask}'
                })
            
            if not self.instance:
                if Equipment.objects.filter(
                    equipment_type=equipment_type,
                    serial_number=serial_number
                ).exists():
                    raise serializers.ValidationError({
                        'serial_number': 'Оборудование с таким серийным номером уже существует'
                    })
            elif self.instance and (
                self.instance.equipment_type != equipment_type or 
                self.instance.serial_number != serial_number
            ):
                if Equipment.objects.filter(
                    equipment_type=equipment_type,
                    serial_number=serial_number
                ).exclude(id=self.instance.id).exists():
                    raise serializers.ValidationError({
                        'serial_number': 'Оборудование с таким серийным номером уже существует'
                    })
        
        return attrs


class EquipmentCreateSerializer(serializers.Serializer):
    """
    Сериализатор для создания оборудования.
    
    Поддерживает создание одной записи или массива записей.
    """
    
    equipment_type = serializers.PrimaryKeyRelatedField(
        queryset=EquipmentType.objects.all()
    )
    serial_numbers = serializers.ListField(
        child=serializers.CharField(max_length=100),
        min_length=1,
        help_text="Массив серийных номеров для создания"
    )
    note = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Примечание для всех создаваемых записей"
    )
    
    def validate(self, attrs):
        """
        Валидирует данные для создания оборудования.
        """
        equipment_type = attrs.get('equipment_type')
        serial_numbers = attrs.get('serial_numbers', [])
        
        validation_errors = []
        valid_serial_numbers = []
        
        for serial_number in serial_numbers:
            errors = []
            
            if not equipment_type.validate_serial_number(serial_number):
                errors.append(f'не соответствует маске {equipment_type.serial_mask}')
            
            if Equipment.objects.filter(
                equipment_type=equipment_type,
                serial_number=serial_number
            ).exists():
                errors.append('уже существует в базе данных')
            
            if serial_number in valid_serial_numbers:
                errors.append('дублируется в текущем запросе')
            
            if errors:
                validation_errors.append({
                    'serial_number': serial_number,
                    'errors': errors
                })
            else:
                valid_serial_numbers.append(serial_number)
        
        if validation_errors:
            raise serializers.ValidationError({
                'validation_errors': validation_errors,
                'message': 'Обнаружены ошибки валидации серийных номеров'
            })
        
        attrs['valid_serial_numbers'] = valid_serial_numbers
        return attrs
    
    @transaction.atomic
    def create(self, validated_data):
        """
        Создает записи оборудования.
        """
        equipment_type = validated_data['equipment_type']
        serial_numbers = validated_data['valid_serial_numbers']
        note = validated_data.get('note', '')
        
        equipment_list = []
        for serial_number in serial_numbers:
            equipment = Equipment(
                equipment_type=equipment_type,
                serial_number=serial_number,
                note=note
            )
            equipment_list.append(equipment)
        
        created_equipment = Equipment.objects.bulk_create(equipment_list)
        return created_equipment


class EquipmentUpdateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для обновления оборудования.
    """
    
    class Meta:
        model = Equipment
        fields = ['equipment_type', 'serial_number', 'note']
    
    def validate(self, attrs):
        """
        Валидирует данные при обновлении.
        """
        equipment_type = attrs.get('equipment_type', self.instance.equipment_type)
        serial_number = attrs.get('serial_number', self.instance.serial_number)
        
        if not equipment_type.validate_serial_number(serial_number):
            raise serializers.ValidationError({
                'serial_number': f'Серийный номер не соответствует маске {equipment_type.serial_mask}'
            })
        
        if Equipment.objects.filter(
            equipment_type=equipment_type,
            serial_number=serial_number
        ).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError({
                'serial_number': 'Оборудование с таким серийным номером уже существует'
            })
        
        return attrs 
import django_filters
from .models import Equipment, EquipmentType


class EquipmentFilter(django_filters.FilterSet):
    """
    Фильтр для оборудования.
    
    Поддерживает поиск по различным полям оборудования.
    """
    
    equipment_type = django_filters.ModelChoiceFilter(
        queryset=EquipmentType.objects.all(),
        help_text="Фильтр по типу оборудования"
    )
    
    equipment_type_name = django_filters.CharFilter(
        field_name='equipment_type__name',
        lookup_expr='exact',
        help_text="Поиск по точному названию типа оборудования"
    )
    
    serial_number = django_filters.CharFilter(
        lookup_expr='exact',
        help_text="Поиск по точному серийному номеру"
    )
    
    note = django_filters.CharFilter(
        lookup_expr='exact',
        help_text="Поиск по точному примечанию"
    )
    
    equipment_type_name_contains = django_filters.CharFilter(
        field_name='equipment_type__name',
        lookup_expr='icontains',
        help_text="Поиск по частичному совпадению в названии типа оборудования"
    )
    
    serial_number_contains = django_filters.CharFilter(
        field_name='serial_number',
        lookup_expr='icontains',
        help_text="Поиск по частичному совпадению в серийном номере"
    )
    
    note_contains = django_filters.CharFilter(
        field_name='note',
        lookup_expr='icontains',
        help_text="Поиск по частичному совпадению в примечании"
    )
    
    created_after = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte',
        help_text="Показать оборудование, созданное после указанной даты"
    )
    
    created_before = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte',
        help_text="Показать оборудование, созданное до указанной даты"
    )
    
    class Meta:
        model = Equipment
        fields = [
            'equipment_type',
            'equipment_type_name',
            'serial_number',
            'note',
            'equipment_type_name_contains',
            'serial_number_contains', 
            'note_contains',
            'created_after',
            'created_before'
        ] 
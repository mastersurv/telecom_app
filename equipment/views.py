from django.shortcuts import render
from rest_framework import generics, status, filters, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import Equipment, EquipmentType
from .serializers import (
    EquipmentSerializer,
    EquipmentCreateSerializer,
    EquipmentUpdateSerializer,
    EquipmentTypeSerializer
)
from .filters import EquipmentFilter
from .pagination import CustomPageNumberPagination


class EquipmentListCreateView(generics.ListCreateAPIView):
    """
    API endpoint для получения списка оборудования и создания нового.
    
    GET: возвращает пагинированный список оборудования с возможностью поиска
    POST: создает новое оборудование (одну или несколько записей)
    """
    
    queryset = Equipment.objects.select_related('equipment_type').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = EquipmentFilter
    search_fields = ['serial_number', 'note', 'equipment_type__name']
    ordering_fields = ['created_at', 'updated_at', 'serial_number']
    ordering = ['-created_at']
    pagination_class = CustomPageNumberPagination
    
    def get_serializer_class(self):
        """
        Возвращает соответствующий сериализатор в зависимости от действия.
        """
        if self.request.method == 'POST':
            return EquipmentCreateSerializer
        return EquipmentSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Создает новое оборудование.
        
        Поддерживает создание множественных записей через массив серийных номеров.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            created_equipment = serializer.save()
            
            response_serializer = EquipmentSerializer(created_equipment, many=True)
            
            return Response({
                'message': f'Успешно создано {len(created_equipment)} единиц оборудования',
                'data': response_serializer.data,
                'count': len(created_equipment)
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'error': 'Ошибка при создании оборудования',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class EquipmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint для работы с отдельной единицей оборудования.
    
    GET: получение данных по ID
    PUT: редактирование записи
    DELETE: мягкое удаление записи
    """
    
    queryset = Equipment.objects.select_related('equipment_type').all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        """
        Возвращает соответствующий сериализатор в зависимости от действия.
        """
        if self.request.method in ['PUT', 'PATCH']:
            return EquipmentUpdateSerializer
        return EquipmentSerializer
    
    def destroy(self, request, *args, **kwargs):
        """
        Выполняет мягкое удаление оборудования.
        """
        instance = self.get_object()
        
        if instance.is_deleted:
            return Response({
                'error': 'Оборудование уже удалено'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        instance.soft_delete()
        
        return Response({
            'message': 'Оборудование успешно удалено',
            'deleted_at': instance.deleted_at
        }, status=status.HTTP_200_OK)


class EquipmentTypeViewSet(viewsets.ModelViewSet):
    """
    ViewSet для полноценного REST API работы с типами оборудования.
    
    Поддерживает все CRUD операции:
    GET /api/equipment/types/ - список типов
    POST /api/equipment/types/ - создание нового типа
    GET /api/equipment/types/{id}/ - получение типа по ID
    PUT /api/equipment/types/{id}/ - обновление типа
    PATCH /api/equipment/types/{id}/ - частичное обновление типа
    DELETE /api/equipment/types/{id}/ - удаление типа
    """
    
    queryset = EquipmentType.objects.prefetch_related('equipment').all()
    serializer_class = EquipmentTypeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'serial_mask']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    pagination_class = CustomPageNumberPagination
    
    def get_queryset(self):
        """
        Фильтрация типов оборудования по query параметрам.
        """
        queryset = super().get_queryset()
        
        name = self.request.query_params.get('name')
        if name:
            queryset = queryset.filter(name__exact=name)
        
        serial_mask = self.request.query_params.get('serial_mask')
        if serial_mask:
            queryset = queryset.filter(serial_mask__exact=serial_mask)
        
        return queryset


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def equipment_stats(request):
    """
    API endpoint для получения статистики по оборудованию.
    
    Возвращает общее количество оборудования, количество по типам и т.д.
    """
    
    total_equipment = Equipment.objects.count()
    total_deleted = Equipment.all_objects.filter(deleted_at__isnull=False).count()
    total_types = EquipmentType.objects.count()
    
    type_stats = []
    for equipment_type in EquipmentType.objects.prefetch_related('equipment'):
        type_stats.append({
            'id': equipment_type.id,
            'name': equipment_type.name,
            'equipment_count': equipment_type.equipment.count(),
            'serial_mask': equipment_type.serial_mask
        })
    
    return Response({
        'total_equipment': total_equipment,
        'total_deleted': total_deleted,
        'total_active': total_equipment,
        'total_types': total_types,
        'type_statistics': type_stats
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def restore_equipment(request, pk):
    """
    API endpoint для восстановления мягко удаленного оборудования.
    """
    
    try:
        equipment = Equipment.all_objects.get(pk=pk)
    except Equipment.DoesNotExist:
        return Response({
            'error': 'Оборудование не найдено'
        }, status=status.HTTP_404_NOT_FOUND)
    
    if not equipment.is_deleted:
        return Response({
            'error': 'Оборудование не удалено'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    equipment.restore()
    
    serializer = EquipmentSerializer(equipment)
    return Response({
        'message': 'Оборудование успешно восстановлено',
        'data': serializer.data
    }, status=status.HTTP_200_OK)

from django.contrib import admin
from .models import EquipmentType, Equipment


@admin.register(EquipmentType)
class EquipmentTypeAdmin(admin.ModelAdmin):
    """
    Админ панель для типов оборудования.
    """
    
    list_display = ['id', 'name', 'serial_mask', 'equipment_count', 'created_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['name', 'serial_mask']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['name']
    
    def equipment_count(self, obj):
        """
        Возвращает количество единиц оборудования данного типа.
        """
        return obj.equipment.count()
    
    equipment_count.short_description = 'Количество оборудования'


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    """
    Админ панель для оборудования.
    """
    
    list_display = [
        'id', 
        'equipment_type', 
        'serial_number', 
        'note_preview',
        'is_deleted',
        'created_at'
    ]
    list_filter = [
        'equipment_type',
        'created_at',
        'updated_at',
        'deleted_at'
    ]
    search_fields = ['serial_number', 'note', 'equipment_type__name']
    readonly_fields = ['created_at', 'updated_at', 'deleted_at']
    ordering = ['-created_at']
    raw_id_fields = ['equipment_type']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('equipment_type', 'serial_number', 'note')
        }),
        ('Системная информация', {
            'fields': ('created_at', 'updated_at', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )
    
    def note_preview(self, obj):
        """
        Возвращает краткое превью примечания.
        """
        if obj.note:
            return obj.note[:50] + '...' if len(obj.note) > 50 else obj.note
        return '-'
    
    note_preview.short_description = 'Примечание'
    
    def is_deleted(self, obj):
        """
        Показывает статус удаления записи.
        """
        return obj.deleted_at is not None
    
    is_deleted.boolean = True
    is_deleted.short_description = 'Удалено'
    
    def get_queryset(self, request):
        """
        Возвращает QuerySet с учетом удаленных записей.
        """
        return Equipment.all_objects.select_related('equipment_type')
    
    actions = ['soft_delete_selected', 'restore_selected']
    
    def soft_delete_selected(self, request, queryset):
        """
        Мягкое удаление выбранных записей.
        """
        count = 0
        for obj in queryset:
            if not obj.is_deleted:
                obj.soft_delete()
                count += 1
        
        self.message_user(request, f'Мягко удалено {count} записей.')
    
    soft_delete_selected.short_description = 'Мягко удалить выбранные записи'
    
    def restore_selected(self, request, queryset):
        """
        Восстановление выбранных записей.
        """
        count = 0
        for obj in queryset:
            if obj.is_deleted:
                obj.restore()
                count += 1
        
        self.message_user(request, f'Восстановлено {count} записей.')
    
    restore_selected.short_description = 'Восстановить выбранные записи'

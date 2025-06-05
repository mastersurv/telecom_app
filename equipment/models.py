from django.db import models
from django.core.validators import RegexValidator
import re


class EquipmentType(models.Model):
    """
    Модель типа оборудования.
    
    Содержит информацию о типе оборудования и маске серийного номера.
    """
    
    name = models.CharField(
        max_length=255,
        verbose_name="Наименование типа оборудования",
        help_text="Название типа оборудования (например, TP-Link TL-WR74)"
    )
    serial_mask = models.CharField(
        max_length=50,
        verbose_name="Маска серийного номера",
        help_text="Маска для валидации серийных номеров (например, XXAAAAAXAA)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'equipment_types'
        verbose_name = "Тип оборудования"
        verbose_name_plural = "Типы оборудования"
        ordering = ['name']
    
    def __str__(self) -> str:
        return str(self.name)
    
    def get_regex_pattern(self) -> str:
        """
        Преобразует маску серийного номера в регулярное выражение.
        
        N – цифра от 0 до 9
        A – прописная буква латинского алфавита  
        a – строчная буква латинского алфавита
        X – прописная буква латинского алфавита либо цифра от 0 до 9
        Z – символ из списка: "-", "_", "@"
        """
        pattern = ""
        for char in str(self.serial_mask):
            if char == 'N':
                pattern += r'[0-9]'
            elif char == 'A':
                pattern += r'[A-Z]'
            elif char == 'a':
                pattern += r'[a-z]'
            elif char == 'X':
                pattern += r'[A-Z0-9]'
            elif char == 'Z':
                pattern += r'[-_@]'
            else:
                pattern += re.escape(char)
        return f'^{pattern}$'
    
    def validate_serial_number(self, serial_number: str) -> bool:
        """
        Валидирует серийный номер согласно маске.
        
        Args:
            serial_number (str): Серийный номер для валидации
            
        Returns:
            bool: True если номер соответствует маске, False иначе
        """
        pattern = self.get_regex_pattern()
        return bool(re.match(pattern, serial_number))


class EquipmentManager(models.Manager):
    """
    Менеджер для модели Equipment, который исключает удаленные записи.
    """
    
    def get_queryset(self):
        """
        Возвращает QuerySet, исключающий записи с deleted_at != None.
        """
        return super().get_queryset().filter(deleted_at__isnull=True)
    
    def with_deleted(self):
        """
        Возвращает QuerySet со всеми записями, включая удаленные.
        """
        return super().get_queryset()
    
    def deleted_only(self):
        """
        Возвращает только удаленные записи.
        """
        return super().get_queryset().filter(deleted_at__isnull=False)


class DeletedEquipmentManager(models.Manager):
    """
    Менеджер для получения только удаленных записей оборудования.
    """
    
    def get_queryset(self):
        """
        Возвращает QuerySet только с удаленными записями.
        """
        return super().get_queryset().filter(deleted_at__isnull=False)


class Equipment(models.Model):
    """
    Модель оборудования.
    
    Содержит информацию об отдельной единице оборудования.
    """
    
    equipment_type = models.ForeignKey(
        EquipmentType,
        on_delete=models.CASCADE,
        related_name='equipment',
        verbose_name="Тип оборудования"
    )
    serial_number = models.CharField(
        max_length=100,
        verbose_name="Серийный номер",
        help_text="Уникальный серийный номер оборудования"
    )
    note = models.TextField(
        blank=True,
        null=True,
        verbose_name="Примечание",
        help_text="Дополнительная информация об оборудовании"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Дата удаления",
        help_text="Дата мягкого удаления записи"
    )
    
    objects = EquipmentManager()
    deleted_objects = DeletedEquipmentManager()
    all_objects = models.Manager()
    
    class Meta:
        db_table = 'equipment'
        verbose_name = "Оборудование"
        verbose_name_plural = "Оборудование"
        unique_together = ('equipment_type', 'serial_number')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['equipment_type']),
            models.Index(fields=['created_at']),
            models.Index(fields=['deleted_at']),
        ]
    
    def __str__(self) -> str:
        return f"{self.equipment_type.name} - {self.serial_number}"
    
    def soft_delete(self):
        """
        Выполняет мягкое удаление записи.
        """
        from django.utils import timezone
        self.deleted_at = timezone.now()
        self.save()
    
    def restore(self):
        """
        Восстанавливает мягко удаленную запись.
        """
        self.deleted_at = None
        self.save()
    
    @property
    def is_deleted(self):
        """
        Проверяет, удалена ли запись.
        
        Returns:
            bool: True если запись удалена, False иначе
        """
        return self.deleted_at is not None

from django.urls import path
from . import views

app_name = 'equipment'

urlpatterns = [
    path('', views.EquipmentListCreateView.as_view(), name='equipment-list-create'),
    path('<int:pk>/', views.EquipmentDetailView.as_view(), name='equipment-detail'),
    path('<int:pk>/restore/', views.restore_equipment, name='equipment-restore'),
    
    path('type/', views.EquipmentTypeListView.as_view(), name='equipment-type-list'),
    
    path('stats/', views.equipment_stats, name='equipment-stats'),
] 
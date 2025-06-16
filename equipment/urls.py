from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'equipment'

router = DefaultRouter()
router.register(r'types', views.EquipmentTypeViewSet, basename='equipment-type')

urlpatterns = [
    path('', views.EquipmentListCreateView.as_view(), name='equipment-list-create'),
    path('<int:pk>/', views.EquipmentDetailView.as_view(), name='equipment-detail'),
    path('<int:pk>/restore/', views.restore_equipment, name='equipment-restore'),
    
    path('', include(router.urls)),
    
    path('stats/', views.equipment_stats, name='equipment-stats'),
] 
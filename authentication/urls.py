from django.urls import path
from . import views

app_name = 'authentication'

urlpatterns = [
    path('login/', views.login, name='login'),
    path('refresh/', views.refresh_token, name='refresh'),
    path('profile/', views.profile, name='profile'),
] 
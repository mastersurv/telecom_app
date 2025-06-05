from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('api/equipment/', include('equipment.urls')),
    path('api/user/', include('authentication.urls')),
    
    path('', views.index, name='index'),
]

if settings.DEBUG:
    urlpatterns += [
        re_path(r'^frontend/(?P<path>.*)$', serve, {
            'document_root': settings.BASE_DIR / 'frontend',
        }),
    ]
    
    urlpatterns += [
        path('app.js', views.frontend_static, {'path': 'app.js'}, name='app-js'),
        path('style.css', views.frontend_static, {'path': 'style.css'}, name='style-css'),
    ]
    
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    if hasattr(settings, 'MEDIA_URL') and hasattr(settings, 'MEDIA_ROOT'):
        urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.shortcuts import render
from django.http import FileResponse, Http404, HttpResponse
from django.conf import settings
from django.views.generic import TemplateView
from django.views.static import serve
import os
import mimetypes


def index(request):
    """
    Отдает главную страницу frontend приложения.
    """
    try:
        frontend_path = os.path.join(settings.BASE_DIR, 'frontend', 'index.html')
        if os.path.exists(frontend_path):
            with open(frontend_path, 'r', encoding='utf-8') as f:
                content = f.read()
            response = HttpResponse(content, content_type='text/html; charset=utf-8')
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
            return response
        else:
            raise Http404("Frontend файл не найден")
    except Exception as e:
        raise Http404(f"Ошибка загрузки frontend: {str(e)}")


def frontend_static(request, path):
    """
    Обслуживает статические файлы frontend с правильными MIME типами.
    """
    try:
        file_path = os.path.join(settings.BASE_DIR, 'frontend', path)
        if os.path.exists(file_path):
            mime_type, _ = mimetypes.guess_type(file_path)
            if mime_type is None:
                if path.endswith('.js'):
                    mime_type = 'application/javascript'
                elif path.endswith('.css'):
                    mime_type = 'text/css'
                else:
                    mime_type = 'application/octet-stream'
            
            with open(file_path, 'rb') as f:
                response = HttpResponse(f.read(), content_type=mime_type)
                response['Access-Control-Allow-Origin'] = '*'
                response['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
                response['Access-Control-Allow-Headers'] = 'Content-Type'
                return response
        else:
            raise Http404(f"Файл {path} не найден")
    except Exception as e:
        raise Http404(f"Ошибка загрузки файла {path}: {str(e)}")


class FrontendView(TemplateView):
    """
    Альтернативный view для frontend с использованием TemplateView.
    """
    template_name = 'index.html'
    
    def get_template_names(self):
        """
        Возвращает путь к шаблону frontend.
        """
        return [os.path.join(settings.BASE_DIR, 'frontend', 'index.html')] 
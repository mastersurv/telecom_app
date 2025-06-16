from rest_framework.pagination import PageNumberPagination


class CustomPageNumberPagination(PageNumberPagination):
    """
    Кастомная пагинация с настраиваемым размером страницы.
    
    Позволяет клиенту указывать размер страницы через параметр 'page_size'.
    Максимальный размер страницы ограничен 100 элементами.
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    page_size_query_description = 'Количество записей на странице (максимум 100)' 
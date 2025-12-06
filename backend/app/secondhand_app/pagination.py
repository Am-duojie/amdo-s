from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class CustomPageNumberPagination(PageNumberPagination):
    """自定义分页类，支持客户端指定每页数量"""
    page_size = 20  # 默认每页数量
    page_size_query_param = 'page_size'  # 允许客户端通过这个参数指定每页数量
    max_page_size = 100  # 每页最大数量限制












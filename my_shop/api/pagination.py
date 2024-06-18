from rest_framework.pagination import PageNumberPagination


class ProductsPagination(PageNumberPagination):
    page_size = 5


class ReviewsPagination(PageNumberPagination):
    page_size = 2


class CategoryManufacturerPagination(PageNumberPagination):
    page_size = 5

from django.contrib.auth import get_user_model
from django.db.models import Avg, Count, Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from api.pagination import (CategoryManufacturerPagination, ProductsPagination,
                            ReviewsPagination)
from api.permissions import IsAdminStaffAuthorReadOnly
from api.serializers import (CategorySerializer, EmailCodeSerializer,
                             GetTokenSerializer, ManufacturerSerializer,
                             ProductDetailSerializer, ProductSerializer,
                             ReviewSerializer, UserRegistrationSerializer)
from api.user_auth_utils import get_tokens_for_user
from main.filters import ProductFilter
from main.models import Category, Manufacturer, Product, Review

User = get_user_model()


@api_view(["POST"])
@permission_classes([AllowAny])
def email_send_confirmation_code(request):
    """Представление для получения кода подтверждения."""
    serializer = EmailCodeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([AllowAny])
def user_signup(request):
    """Представление для получения кода подтверждения."""
    serializer = UserRegistrationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    response_serializer = UserRegistrationSerializer(
        user, context={"request": request}
    )
    return Response(response_serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([AllowAny])
def get_token(request):
    """Представление для получения токена."""
    serializer = GetTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(
        User, username=serializer.validated_data["username"]
    )
    token = get_tokens_for_user(user)
    return Response(token, status=status.HTTP_200_OK)


class RetrieveListViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    pass


class ProductViewSet(RetrieveListViewSet):
    """Представление для получения товаров."""

    queryset = Product.objects.filter(is_active=True).annotate(
        num_shop=Count("shop", distinct=True),
        num_products=Sum(
            "shopproduct__shopproductcolourproduct__quantity", distinct=True
        ),
        rating=Avg("reviews__rating"),
    )
    serializer_class = ProductSerializer
    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    )
    filterset_class = ProductFilter
    search_fields = ("name",)
    ordering_fields = ("name", "actual_price", "rating")
    lookup_url_kwarg = "product_id"
    pagination_class = ProductsPagination

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ProductDetailSerializer
        return ProductSerializer

    # Получение 5 последних отзывов
    @action(detail=False)
    def reviews(self, request):
        reviews = Review.objects.all()[:5]
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)


class ReviewViewSet(viewsets.ModelViewSet):
    """Представление для отзывов."""

    serializer_class = ReviewSerializer
    http_method_names = ("get", "post", "patch", "delete")
    pagination_class = ReviewsPagination
    permission_classes = (IsAdminStaffAuthorReadOnly,)
    filter_backends = (filters.OrderingFilter, DjangoFilterBackend)
    ordering_fields = ("created_at", "rating")
    filterset_fields = ("rating",)

    def get_product(self):
        return get_object_or_404(Product, id=self.kwargs.get("product_id"))

    # Получаем все отзывы, связанные с указанным товаром
    def get_queryset(self):
        return self.get_product().reviews.all()

    # Добавляем автора в отзыв при сохранении
    def perform_create(self, serializer):
        serializer.save(author=self.request.user, product=self.get_product())


class CategoriesViewSet(viewsets.ModelViewSet):
    """Представление для категорий."""

    queryset = Category.objects.filter(is_active=True)
    pagination_class = CategoryManufacturerPagination
    serializer_class = CategorySerializer
    permission_classes = (IsAdminStaffAuthorReadOnly,)

    def get_queryset(self):
        """Отдаем все категории только сотрудникам."""
        if self.request.user.is_superuser or self.request.user.is_staff:
            return Category.objects.all()
        return super().get_queryset()


class ManufacrurerViewSet(viewsets.ModelViewSet):
    """Представление для получения производителей."""

    queryset = Manufacturer.objects.filter(is_active=True)
    pagination_class = CategoryManufacturerPagination
    serializer_class = ManufacturerSerializer
    permission_classes = (IsAdminStaffAuthorReadOnly,)

    def get_queryset(self):
        """Отдаем всех производителей только сотрудникам."""
        if self.request.user.is_superuser or self.request.user.is_staff:
            return Manufacturer.objects.all()
        return super().get_queryset()

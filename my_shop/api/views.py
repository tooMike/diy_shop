from django.contrib.auth import get_user_model
from django.db.models import Avg, Count, OuterRef, Subquery, Sum
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.code_schemas import product_detail_code_schema
from api.mixins import ListRetrieveViewSet, ListViewSet
from api.permissions import IsAdminStaffOwnerReadOnly, IsOwner
from api.serializers import (CategorySerializer, EmailCodeSerializer,
                             GetTokenSerializer, ManufacturerSerializer,
                             OrderCreateSerializer, OrderListSerializer,
                             OrderRetriveSerializer, ProductDetailSerializer,
                             ProductsListSerializer, ReviewSerializer,
                             ShoppingCartCreateSerializer,
                             ShoppingCartListSerializer,
                             ShoppingCartUpdateSerializer,
                             UserRegistrationSerializer)
from api.user_auth_utils import get_tokens_for_user
from main.filters import ProductFilter
from main.models import Category, ColorProductShop, Manufacturer, Product
from orders.models import Order
from shopping_cart.models import ShoppingCart

User = get_user_model()


@swagger_auto_schema(
    method="post", request_body=EmailCodeSerializer, security=[]
)
@api_view(["POST"])
@permission_classes([AllowAny])
def email_send_confirmation_code(request):
    """Представление для отправки кода подтверждения на емейл."""
    serializer = EmailCodeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method="post", request_body=UserRegistrationSerializer, security=[]
)
@api_view(["POST"])
@permission_classes([AllowAny])
def user_signup(request):
    """Представление для регистрации пользователя."""
    serializer = UserRegistrationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    response_serializer = UserRegistrationSerializer(
        user, context={"request": request}
    )
    return Response(response_serializer.data, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method="post", request_body=GetTokenSerializer, security=[]
)
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

@method_decorator(
    name="retrieve",
    decorator=swagger_auto_schema(
        responses={
            200: openapi.Response(
                "Product retrieved", product_detail_code_schema
            )
        }
    )
)
class ProductsViewSet(ListRetrieveViewSet):
    """Представление для товаров."""

    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    )
    filterset_class = ProductFilter
    search_fields = ("name", "description")
    ordering_fields = ("name", "actual_price", "rating")
    pagination_class = LimitOffsetPagination

    def get_serializer_class(self):
        if self.action == "list":
            return ProductsListSerializer
        else:
            return ProductDetailSerializer

    def get_queryset(self):
        queryset = Product.objects.filter(
            is_active=True,
            # Отдает только товары, которые есть в магазинах
            colorproduct__colorproductshop__quantity__gt=0,
        ).select_related(
            "manufacturer",
            "category",
        )
        if self.action == "list":
            queryset = queryset.annotate(
                # Добавляем количество магазинов, где есть товар
                num_shop=Count(
                    "colorproduct__colorproductshop__shop", distinct=True
                ),
                # Добавляем доступное количество товаров
                num_products=Subquery(
                    ColorProductShop.objects.filter(
                        colorproduct__product=OuterRef("pk")
                    )
                    .values("colorproduct__product")
                    .annotate(total=Sum("quantity"))
                    .values("total")
                ),
                # Добавляем средний рейтинг
                rating=Avg("reviews__rating"),
            )
        else:
            queryset = queryset.annotate(
                reviews_count=Count("reviews"),
            ).select_related("manufacturer__country")

        return queryset


class ReviewViewSet(viewsets.ModelViewSet):
    """Представление для отзывов."""

    serializer_class = ReviewSerializer
    http_method_names = ["get", "post", "patch", "delete"]
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAdminStaffOwnerReadOnly,)
    filter_backends = (filters.OrderingFilter, DjangoFilterBackend)
    ordering_fields = ("created_at", "rating")
    filterset_fields = ("rating",)

    def get_product(self):
        return get_object_or_404(Product, id=self.kwargs.get("product_id"))

    def get_queryset(self):
        """Получаем только отзывы, связанные с выбранным товаром"""
        return self.get_product().reviews.all()

    # Добавляем автора в отзыв при сохранении
    def perform_create(self, serializer):
        serializer.save(author=self.request.user, product=self.get_product())


class CategoriesViewSet(ListViewSet):
    """Представление для получения списка категорий."""

    pagination_class = LimitOffsetPagination
    serializer_class = CategorySerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Возвращаем только активные категории."""
        return Category.objects.filter(is_active=True)


class ManufacturerViewSet(ListViewSet):
    """Представление для получения списка производителей."""

    pagination_class = LimitOffsetPagination
    serializer_class = ManufacturerSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Возвращаем только активных производителей."""
        return Manufacturer.objects.filter(is_active=True)


class ShoppingCartViewSet(viewsets.ModelViewSet):
    """Представление для корзины товаров."""

    permission_classes = (IsOwner,)
    http_method_names = ["get", "post", "patch", "delete"]
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        """Возвращаем только корзину текущего пользователя."""
        return ShoppingCart.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "create":
            return ShoppingCartCreateSerializer
        elif self.action == "partial_update":
            return ShoppingCartUpdateSerializer
        else:
            return ShoppingCartListSerializer

    def get_permissions(self):
        """
        Создание корзины разрешаем всем аутентифицированным пользователя.
        Остальные операции разрешаем только автору корзины.
        """
        if self.action == "create":
            return (IsAuthenticated(),)
        return super().get_permissions()


class OrderViewSet(viewsets.ModelViewSet):
    """Представление для заказов."""

    permission_classes = (IsOwner,)
    http_method_names = ["get", "post"]
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        """Возвращаем только заказы текущего пользователя."""
        return Order.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "create":
            return OrderCreateSerializer
        elif self.action == "retrieve":
            return OrderRetriveSerializer
        else:
            return OrderListSerializer

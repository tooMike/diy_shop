from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, render
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from api.serializers import (EmailCodeSerializer, GetTokenSerializer,
                             ProductSerializer, UserRegistrationSerializer)
from api.user_auth_utils import get_tokens_for_user
from main.models import Product


User = get_user_model()

@api_view(["POST"])
@permission_classes([AllowAny])
def email_send_confirmation_code(request):
    """
    Представление для получения кода подтверждения
    """
    data = request.data
    serializer = EmailCodeSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([AllowAny])
def user_signup(request):
    """
    Представление для получения кода подтверждения
    """
    data = request.data
    serializer = UserRegistrationSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    response_serializer = UserRegistrationSerializer(user, context={'request': request})
    return Response(response_serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([AllowAny])
def get_token(request):
    """Представление для получения токена."""
    serializer = GetTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(
        User,
        username=serializer.validated_data["username"]
    )
    token = get_tokens_for_user(user)
    return Response(token, status=status.HTTP_200_OK)


class RetrieveListViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    pass


class ProductViewSet(RetrieveListViewSet):
    serializer_class = ProductSerializer

    def get_queryset(self):
        queryset = Product.objects.all()
        category = self.request.query_params.get('category')
        manufacturer = self.request.query_params.get('manufacturer')

        if category:
            return queryset.filter(category__slug=category)
        elif manufacturer:
            return queryset.filter(manufacturer__slug=manufacturer)
        return queryset

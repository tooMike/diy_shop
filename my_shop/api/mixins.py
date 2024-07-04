from rest_framework import mixins, viewsets


class ListViewSet(
    mixins.ListModelMixin, viewsets.GenericViewSet
):
    """Миксин для списковых представлений."""


class RetrieveViewSet(
    mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    """Миксин для конкретного представления."""

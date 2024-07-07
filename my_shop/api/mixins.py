from rest_framework import mixins, viewsets


class ListViewSet(
    mixins.ListModelMixin, viewsets.GenericViewSet
):
    """Миксин для списковых представлений."""


class ListRetrieveViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    """Миксин для детального и спискового представления."""

from drf_yasg import openapi

manufacturer_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "id": openapi.Schema(type=openapi.TYPE_INTEGER),
        "name": openapi.Schema(type=openapi.TYPE_STRING),
        "country": openapi.Schema(type=openapi.TYPE_STRING),
        "slug": openapi.Schema(type=openapi.TYPE_STRING),
        "is_active": openapi.Schema(type=openapi.TYPE_BOOLEAN),
    },
)

item_offline_shops_data_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "shop": openapi.Schema(
            type=openapi.TYPE_STRING, example="Санкт-Петербург пр. Мира"
        ),
        "shop_id": openapi.Schema(type=openapi.TYPE_INTEGER),
        "quantity": openapi.Schema(type=openapi.TYPE_INTEGER),
    },
)

offline_shops_data_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "color": openapi.Schema(type=openapi.TYPE_STRING),
        "color_id": openapi.Schema(type=openapi.TYPE_INTEGER),
        "items": openapi.Schema(
            type=openapi.TYPE_ARRAY, items=item_offline_shops_data_schema
        ),
    },
)

internet_shop_data = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "color": openapi.Schema(type=openapi.TYPE_STRING),
        "color_id": openapi.Schema(type=openapi.TYPE_INTEGER),
        "quantity": openapi.Schema(type=openapi.TYPE_INTEGER),
    },
)

product_detail_code_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "id": openapi.Schema(type=openapi.TYPE_INTEGER),
        "name": openapi.Schema(type=openapi.TYPE_STRING),
        "price": openapi.Schema(type=openapi.TYPE_STRING),
        "sale": openapi.Schema(type=openapi.TYPE_INTEGER),
        "actual_price": openapi.Schema(type=openapi.TYPE_STRING),
        "image": openapi.Schema(
            type=openapi.TYPE_STRING, example="https://example.com/image.jpg"
        ),
        "category": openapi.Schema(type=openapi.TYPE_STRING),
        "manufacturer": manufacturer_schema,
        "offline_shops_data": openapi.Schema(
            type=openapi.TYPE_ARRAY, items=offline_shops_data_schema
        ),
        "internet_shop_data": openapi.Schema(
            type=openapi.TYPE_ARRAY, items=internet_shop_data
        ),
        "rating": openapi.Schema(type=openapi.TYPE_INTEGER),
    },
    required=["product_id"],
)

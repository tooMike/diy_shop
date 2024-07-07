# Описание

DIY Shop – это полноценный интернет магазин инструмента и сопутствующих товаров для DIY. 

С текущей работающей версией проекта можно ознакомиться здесь: https://goms603.com/

Документация к API доступна здесь: https://goms603.com/swagger/ или здесь: https://goms603.com/redoc/

Проект реализован на фреймворке Django. Сделана удобная навигация, фильтрация и сортировка товаров. Также добавлена возможность добавлять рейтинг и  отзывы на товары. Реализована логика добавления, удаления и изменения количества товаров в корзине для анонимных и авторизированных пользователей.

Пользовательский интерфейс реализован на Django-шаблонах. Также частично реализован REST API на Django REST Framework для управления данными через PostgreSQL. Внедрена аутентификация на основе JWT токенов и функционал для импорта данных в БД из JSON-файлов. Для развертывания используются Docker контейнеры и оркестрация Docker Compose. 

Проект находится в стадии разработки. В ближайшее время планируется добавить возможность добавления товаров в избранное, а также исправить существующие баги. Также планируется написать API c использованием фреймворка FastAPI.

# Автор проекта

[Mikhail](https://github.com/tooMike)

# Установка и запуск с Docker

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/tooMike/diy_shop
```

```
cd my_shop
```

Запустить сборку проекта:

```
docker compose up
```

Выполнить сбор статики в контейнере backend:

```
docker compose exec backend python manage.py collectstatic
```

Выполнить миграции в контейнере backend:

```
docker compose exec backend python manage.py migrate
```

Проект будет доступен по адресу

```
http://127.0.0.1:8000/
```

# Добавление тестовых данных в базу данных

Выполнить команду import_data в контейнере backend:

```
docker compose exec backend python manage.py import_data
```

# Спецификация

При локальном запуске документация будет доступна по адресу:

```
http://127.0.0.1:8000/redoc/ или http://127.0.0.1:8000/swagger/
```

# Примеры запросов к API

### Регистрация нового пользователя

Описание метода: Подтвердить email для регистрации нового пользователя в сервисе.

Права доступа: Доступно без токена.

Тип запроса: `POST`

Эндпоинт: `/api/auth/email_verification/`

Обязательные параметры: `email`

Пример запрос:

```
{
  "email": "vpupkin@yandex.ru",
}
```

Пример успешного ответа:

```
{
  "email": "vpupkin@yandex.ru",
}
```

### Получение списка товаров

Права доступа: Аутентифицированные пользователи.

Тип запроса: `GET`

Эндпоинт: `/api/products/`

Доступен поиск по названию и описанию товара: `/api/products/?search=product_name`

Доступны фильтры по минимальной и максимальной цене, магазину, категории и производителю: `/api/products/?min_price=...&max_price=...&shop_id=...&category=...&manufacturer=...`

Доступна сортировка по полям name, actual_price, rating: `/api/products/?ordering=-actual_price,rating,name`


Пример успешного ответа:

```
{
    "count": 40,
    "next": "http://127.0.0.1:8000/api/products/?page=2",
    "previous": null,
    "results": [
        {
            "name": "Дрель Bosch",
            "price": "5000.00",
            "sale": 10,
            "actual_price": "4500.00",
            "image": "http://127.0.0.1:8000/media/product_images/default_image.png",
            "category": "Дрели",
            "manufacturer": "Bosch",
            "num_shop": 8,
            "num_products": 899,
            "rating": null
        },
        ...

    ]
}
```

### Получение информации о конкретном товаре

Права доступа: Аутентифицированные пользователи.

Тип запроса: `GET`

Эндпоинт: `/api/product/1/`

Пример успешного ответа:

```
{
  "id": 0,
  "name": "string",
  "price": "string",
  "sale": 0,
  "actual_price": "string",
  "image": "https://example.com/image.jpg",
  "category": {
    "id": 0,
    "name": "string",
    "description": "string"
  },
  "manufacturer": {
    "id": 0,
    "name": "string",
    "country": "string"
  },
  "offline_shops_data": [
    {
      "color": "string",
      "color_id": 0,
      "items": [
        {
          "shop": "Санкт-Петербург пр. Мира",
          "shop_id": 0,
          "quantity": 0
        }
      ]
    }
  ],
  "internet_shop_data": [
    {
      "color": "string",
      "color_id": 0,
      "quantity": 0
    }
  ],
  "average_rating": 0,
  "reviews_count": 0
}
```

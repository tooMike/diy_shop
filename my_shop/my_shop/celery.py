from __future__ import absolute_import, unicode_literals

import os

from celery import Celery

# Установка default Django settings module для 'celery'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "my_shop.settings")

app = Celery("my_shop")

# Использование строки здесь означает что конфигурационный объект не будет виден в runtime
app.config_from_object("django.conf:settings", namespace="CELERY")

# Загрузка задач из всех зарегистрированных apps в Django
app.autodiscover_tasks()

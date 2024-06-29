import csv
import os
import shutil
from decimal import Decimal

from django.apps import apps
from django.core.management.base import BaseCommand

# Данные для добавления в модели в формате: app:Model:path/to/file.csv
triples = [
    "main:Category:data/categories.csv",
    "main:Country:data/countries.csv",
    "main:Manufacturer:data/manufacturers.csv",
    "main:Colour:data/colours.csv",
    "main:Shop:data/shops.csv",
    "main:Product:data/products.csv",
    "main:ShopProduct:data/shopproduct.csv",
    "main:ColourProduct:data/colourproduct.csv",
    "main:ShopProductColourProduct:data/shopproductcolourproduct.csv",
    "users:MyUser:data/users.csv",
    "main:Review:data/review.csv",
]

# Пути для копирования изображений
image_src_file = "data/default_image.png"
image_dest_directory = "media/product_images"


class Command(BaseCommand):
    help = """
        Загрузка данных из csv-файлов в модели.
        Пример команды: python manage.py import_data
        """

    def handle(self, *args, **options):
        # Копируем файлы с изображениями товаров
        self.copy_file(image_src_file, image_dest_directory)

        for triple in triples:
            parts = triple.split(":")
            if len(parts) == 3:
                app_name, model_name, csv_file_path = parts
                model = apps.get_model(app_name, model_name)
                self.import_data(model, csv_file_path)
            else:
                self.stdout.write(
                    self.style.ERROR(f"Неверный формат: '{triple}'")
                )

    def copy_file(self, src_file, dest_dir):
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        dest_path = os.path.join(dest_dir, os.path.basename(src_file))
        shutil.copy2(src_file, dest_path)
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully copied {src_file} to {dest_path}"
            )
        )

    def import_data(self, model, csv_file_path):
        with open(csv_file_path, newline="", encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile)
            field_names = next(reader)  # Получение заголовков
            for row in reader:
                data = {
                    field_names[i]: (
                        Decimal(row[i])
                        if field_names[i] in ("price", "sale")
                        else row[i]
                    )
                    for i in range(len(field_names))
                }
                # Распаковываем словарь и создаем объект модели
                model.objects.create(**data)

        self.stdout.write(
            self.style.SUCCESS(f"Successfully imported data: {model}")
        )

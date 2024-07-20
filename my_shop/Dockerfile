FROM python:3.9

# Установка рабочего каталога
WORKDIR /app

# Копирование и установка зависимостей
COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir

# Установка supervisor
RUN apt-get update && apt-get install -y supervisor

# Копирование исходного кода приложения
COPY . .

# Копирование конфигурационного файла supervisord
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Команда для запуска supervisord
CMD ["/usr/bin/supervisord"]

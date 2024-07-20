from celery import shared_task
from django.core.mail import send_mail


@shared_task
def send_email_task(subject, message, from_email, recipient_list):
    """Отправка email с кодом подтверждения пользователям."""
    send_mail(subject, message, from_email, recipient_list)

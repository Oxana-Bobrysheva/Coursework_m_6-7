from decouple import config
from django.core.mail import send_mail
from django.utils import timezone
from .models import Mailing, MailingAttempt


def send_mailing(mailing):
    """Функция отправки рассылки и записи попыток"""
    subscribers = mailing.subscribers.all()

    for subscriber in subscribers:
        try:

            result = send_mail(
                mailing.message.subject_of_the_letter,
                mailing.message.letter,
                config('EMAIL_HOST_USER'),
                [subscriber.email],
                fail_silently=False,
            )
            if result == 1:
                MailingAttempt.objects.create(
                    mailing=mailing,
                    status='successful',
                    attempt_time=timezone.now(),
                    server_response='Письмо успешно отправлено'
                )
            else:
                raise Exception("Не удалось отправить письмо")

        except Exception as e:
            # В случае ошибки создаем запись о неуспешной попытке
            MailingAttempt.objects.create(
                mailing=mailing,
                status='failed',
                attempt_time=timezone.now(),
                server_response=str(e)  # Сохраняем текст ошибки
            )

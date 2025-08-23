from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from subscriptions.models import Mailing
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Отправка рассылки по ID'

    def add_arguments(self, parser):
        parser.add_argument('mailing_id', type=int, help='ID рассылки для отправки')

    def handle(self, *args, **kwargs):
        mailing_id = kwargs['mailing_id']

        try:
            mailing = Mailing.objects.get(id=mailing_id)

            self.stdout.write(f"Начинаем отправку рассылки #{mailing.id}")
            self.stdout.write(f"Сообщение: {mailing.message.subject_of_the_letter}")
            self.stdout.write(f"Получателей: {mailing.subscribers.count()}")

            if timezone.now() >= mailing.start_time:
                successful_sends = 0
                failed_sends = 0

                # Реальная логика отправки email
                for subscriber in mailing.subscribers.all():
                    try:
                        # Валидация email
                        validate_email(subscriber.email)

                        # Отправка реального email
                        send_mail(
                            subject=mailing.message.subject_of_the_letter,
                            message=mailing.message.letter,
                            from_email=settings.DEFAULT_FROM_EMAIL,  # Используем настройки из settings.py
                            recipient_list=[subscriber.email],
                            fail_silently=False,
                        )

                        successful_sends += 1
                        self.stdout.write(f"✅ Отправлено на {subscriber.email}")

                    except ValidationError:
                        self.stdout.write(self.style.ERROR(f"❌ Неверный email: {subscriber.email}"))
                        failed_sends += 1
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"❌ Ошибка отправки на {subscriber.email}: {str(e)}"))
                        failed_sends += 1
                        logger.error(f"Error sending email to {subscriber.email}: {e}")

                # Обновляем статус рассылки
                mailing.status = 'started'
                mailing.save()

                self.stdout.write(self.style.SUCCESS(
                    f'✅ Рассылка завершена! Успешно: {successful_sends}, Не отправлено: {failed_sends}'
                ))

            else:
                self.stdout.write(
                    self.style.WARNING('⚠️ Рассылка не может быть отправлена до начала времени отправки!'))
                self.stdout.write(f"Время начала: {mailing.start_time}")
                self.stdout.write(f"Текущее время: {timezone.now()}")

        except Mailing.DoesNotExist:
            self.stdout.write(self.style.ERROR('❌ Рассылка с указанным ID не найдена!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Ошибка при отправке рассылки: {str(e)}'))
            logger.error(f"Error in send_mailing command: {e}")

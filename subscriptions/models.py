from django.conf import settings
from django.db import models
from django.utils import timezone


class Subscriber(models.Model):
    """
       Модель подписчика, представляющая получателя рассылки.
       Поля:
           email (EmailField): Электронная почта подписчика, уникальное значение.
           name (CharField): Имя подписчика, необязательное.
           comment (TextField): Комментарий от подписчика, необязательное.
    """
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=120, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Владелец клиента',
        )
    def __str__(self):
        """Функция возвращает строковое представление подписчика - его email"""
        return self.email


class Message(models.Model):
    """Модель сообщения, представляющая непосредственно рассылку.
    Поля:
        subject_of_the_letter (): Тема письма.
        letter (): Тело письма, его содержимое.
    """
    subject_of_the_letter = models.CharField(max_length=150)
    letter = models.TextField()

    def __str__(self):
        """Функция возвращает строковое представление сообщения - его тему(subject_of_the_letter)"""
        return self.subject_of_the_letter


class Mailing(models.Model):
    STATUS_CHOICES = [
        ('created', 'Создана'),
        ('started', 'Запущена'),
        ('completed', 'Завершена'),
    ]

    start_time = models.DateTimeField(
        verbose_name='Дата и время начала отправки',
        default=timezone.now
    )
    end_time = models.DateTimeField(
        verbose_name='Дата и время окончания отправки'
    )
    status = models.CharField(
        verbose_name='Статус',
        max_length=10,
        choices=STATUS_CHOICES,
        default='created'
    )
    message = models.ForeignKey(
        'Message',
        on_delete=models.CASCADE,
        verbose_name='Сообщение'
    )
    subscribers = models.ManyToManyField(
        'Subscriber',
        verbose_name='Получатели'
    )
    created_at = models.DateTimeField(
        verbose_name='Дата создания',
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        verbose_name='Дата изменения',
        auto_now=True
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Владелец рассылки',
       )
    is_active = models.BooleanField(verbose_name='Активна', default=True)

    class Meta:
        verbose_name = 'рассылка'
        verbose_name_plural = 'рассылки'
        ordering = ['-created_at']

    def __str__(self):
        return f'Рассылка #{self.id} - {self.get_status_display()}'

    def update_status(self):
        """Автоматическое обновление статуса рассылки"""
        now = timezone.now()
        if self.status != 'completed' and now > self.end_time:
            self.status = 'completed'
            self.save()
        elif self.status == 'created' and now >= self.start_time:
            self.status = 'started'
            self.save()

    def get_total_attempts(self):
        """Общее количество попыток отправки"""
        return self.attempts.count()  # Используем related_name='attempts'

    def get_successful_attempts(self):
        """Количество успешных отправок"""
        return self.attempts.filter(status='successful').count()  # Ваш статус 'successful'

    def get_failed_attempts(self):
        """Количество неудачных отправок"""
        return self.attempts.filter(status='failed').count()  # Ваш статус 'failed'

    def get_success_rate(self):
        """Процент успешных отправок"""
        total = self.get_total_attempts()
        if total == 0:
            return 0
        return round((self.get_successful_attempts() / total) * 100, 1)

class MailingAttempt(models.Model):
    STATUS_CHOICES = [
        ('successful', 'Успешно'),
        ('failed', 'Не успешно'),
    ]

    attempt_time = models.DateTimeField(
        verbose_name='Дата и время попытки',
        default=timezone.now
    )
    status = models.CharField(
        verbose_name='Статус',
        max_length=10,
        choices=STATUS_CHOICES
    )
    server_response = models.TextField(
        verbose_name='Ответ почтового сервера',
        blank=True
    )
    mailing = models.ForeignKey(
        Mailing,
        on_delete=models.CASCADE,
        related_name='attempts',
        verbose_name='Рассылка'
    )
    subscriber = models.ForeignKey(
        "Subscriber",
        on_delete=models.CASCADE,
        verbose_name="Подписчик")


    class Meta:
        verbose_name = 'Попытка рассылки'
        verbose_name_plural = 'Попытки рассылок'
        ordering = ['-attempt_time']


    def __str__(self):
        return f'Попытка #{self.id} - {self.get_status_display()}'
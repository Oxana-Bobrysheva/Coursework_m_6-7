from django.db import models


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

    def __str__(self):
        """Функция возвращает строковое представление подписчика - его email"""
        return self.email

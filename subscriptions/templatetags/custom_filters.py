from django import template
from django.contrib.auth.models import Group # noqa: F401

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Фильтр для доступа к элементу словаря по ключу."""
    return dictionary.get(key)

@register.filter
def is_manager(user):
    """Проверяет, является ли пользователь менеджером (в группе 'Manager')."""
    return user.groups.filter(name='Manager').exists()
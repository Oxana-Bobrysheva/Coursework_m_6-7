from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Фильтр для доступа к элементу словаря по ключу."""
    return dictionary.get(key)
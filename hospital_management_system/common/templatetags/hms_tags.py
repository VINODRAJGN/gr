from django import template

register = template.Library()


@register.filter
def split(value, delimiter=","):
    return value.split(delimiter)


@register.filter
def get_item(dictionary, key):
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None

from django import template

register = template.Library()


@register.filter
def percentage(value, total):
    return (value / total) * 100 if total else 0

@register.filter
def round_to_two(value):
    return round(value, 2)

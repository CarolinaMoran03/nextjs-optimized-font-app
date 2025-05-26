from django import template

register = template.Library()

@register.filter(name='times')
def times(number):
    """
    Returns a range of numbers from 1 to the given number.
    Usage in template: {% for i in number|times %}
    """
    try:
        return range(int(number))
    except (ValueError, TypeError):
        return range(0)

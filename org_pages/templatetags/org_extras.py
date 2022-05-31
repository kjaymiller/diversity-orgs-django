from django import template

register = template.Library()

@register.filter(name='classname')
def classname(value):
    return value.__class__.__name__
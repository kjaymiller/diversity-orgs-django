from django import template
from urllib.parse import urlencode

register = template.Library()


@register.filter(name="classname")
def classname(value):
    return value.__class__.__name__


@register.simple_tag
def urlparams(*_, **kwargs):
    safe_args = {k: v for k, v in kwargs.items() if v is not None}
    if safe_args:
        encoded_args = urlencode(safe_args)
        return f'?{encoded_args}'
    return ''
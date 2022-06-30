from django import template
from urllib.parse import urlencode, quote

register = template.Library()


@register.filter(name="classname")
def classname(value):
    return value.__class__.__name__


@register.simple_tag
def urlparams(*_, **kwargs):
    safe_args = {k: v for k, v in kwargs.items() if v is not None}
    if safe_args:
        encoded_args = urlencode(safe_args, quote_via=quote)
        return f'?{encoded_args}'
    return ''
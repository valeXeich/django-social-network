from django import template

register = template.Library()

@register.filter
def get_type(object):
    return type(object)
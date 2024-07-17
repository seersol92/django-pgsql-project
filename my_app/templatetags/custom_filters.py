# todos/templatetags/custom_filters.py

from django import template
from django.utils.timesince import timesince
from django.utils.timezone import now

register = template.Library()

@register.filter(name='time_ago')
def time_ago(value):
    return timesince(value, now())


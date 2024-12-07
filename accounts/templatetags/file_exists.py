import os

from django import template
from django.conf import settings

register = template.Library()


@register.filter(name="file_exists")
def file_exists(filepath):
    return os.path.isfile(os.path.join(settings.MEDIA_ROOT, filepath))

from django import template
from logtailer.models import Filter

register = template.Library()


@register.inclusion_tag('logtailer/templatetags/filters.html')
def filters_select():
    filters = Filter.objects.all()
    return {'filters': filters}
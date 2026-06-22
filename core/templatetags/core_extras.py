from urllib.parse import urlencode

from django import template


register = template.Library()


@register.filter
def split_csv(value):
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


@register.simple_tag(takes_context=True)
def querystring(context, **kwargs):
    query = context["request"].GET.copy()
    for key, value in kwargs.items():
        if value in (None, ""):
            query.pop(key, None)
        else:
            query[key] = value
    return urlencode(query, doseq=True)

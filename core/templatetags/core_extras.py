from urllib.parse import urlencode

from django import template
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

from core.models import Reaction


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


@register.filter(needs_autoescape=True)
def highlight(value, term, autoescape=True):
    text = "" if value is None else str(value)
    needle = "" if term is None else str(term).strip()
    if not needle:
        return conditional_escape(text) if autoescape else text
    escaped = conditional_escape(text) if autoescape else text
    lower_text = str(escaped).lower()
    lower_needle = needle.lower()
    start = lower_text.find(lower_needle)
    if start == -1:
        return escaped
    end = start + len(needle)
    return mark_safe(f"{escaped[:start]}<mark>{escaped[start:end]}</mark>{escaped[end:]}")


@register.simple_tag
def reaction_summary_for(obj):
    if not obj:
        return {}
    from django.contrib.contenttypes.models import ContentType

    content_type = ContentType.objects.get_for_model(obj)
    summary = {choice: 0 for choice, _label in Reaction.ReactionType.choices}
    for reaction_type in Reaction.objects.filter(content_type=content_type, object_id=obj.pk).values_list("reaction_type", flat=True):
        summary[reaction_type] = summary.get(reaction_type, 0) + 1
    return summary

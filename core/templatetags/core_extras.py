from urllib.parse import urlencode
import re

from django import template
from django.utils.html import conditional_escape, escape, linebreaks
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


@register.filter
def render_blog_content(value):
    text = "" if value is None else str(value)
    special_blocks = []

    def stash_code(match):
        language = (match.group(1) or "plaintext").strip().lower()
        aliases = {"django": "django", "html": "xml", "shell": "bash", "sh": "bash", "py": "python"}
        language = aliases.get(language, language)
        code = escape(match.group(2).strip("\r\n"))
        token = f"@@SPECIAL_BLOCK_{len(special_blocks)}@@"
        special_blocks.append(
            '<div class="code-block-wrap">'
            '<button class="code-copy-btn" type="button" aria-label="Copy code" title="Copy code">'
            '<i class="bi bi-copy"></i><span class="visually-hidden">Copy code</span>'
            '</button>'
            f'<pre class="code-block"><code class="language-{escape(language)}">{code}</code></pre>'
            '</div>'
        )
        return token

    fence_pattern = r"```[ \t]*([A-Za-z0-9_-]+)?[ \t]*(?:\r?\n)(.*?)(?:\r?\n)?```"
    without_code = re.sub(fence_pattern, stash_code, text, flags=re.DOTALL)

    def stash_output(match):
        output = escape(match.group(1).strip("\r\n"))
        token = f"@@SPECIAL_BLOCK_{len(special_blocks)}@@"
        special_blocks.append(
            '<div class="command-output-wrap">'
            '<div class="command-output-label"><i class="bi bi-terminal"></i> Output</div>'
            f'<pre class="command-output">{output}</pre>'
            '</div>'
        )
        return token

    without_code = re.sub(r":::[ \t]*output[ \t]*(?:\r?\n)(.*?)(?:\r?\n)?:::", stash_output, without_code, flags=re.DOTALL | re.IGNORECASE)

    def stash_screenshot(match):
        body = match.group(1).strip()
        lines = [line.strip() for line in body.splitlines() if line.strip()]
        if not lines:
            return ""
        image_url = escape(lines[0])
        caption = escape(" ".join(lines[1:])) if len(lines) > 1 else "Command screenshot"
        token = f"@@SPECIAL_BLOCK_{len(special_blocks)}@@"
        special_blocks.append(
            '<figure class="command-screenshot">'
            f'<img src="{image_url}" alt="{caption}">'
            f'<figcaption>{caption}</figcaption>'
            '</figure>'
        )
        return token

    without_code = re.sub(r":::[ \t]*screenshot[ \t]*(?:\r?\n)(.*?)(?:\r?\n)?:::", stash_screenshot, without_code, flags=re.DOTALL | re.IGNORECASE)

    html = linebreaks(escape(without_code))
    for index, block in enumerate(special_blocks):
        token = f"@@SPECIAL_BLOCK_{index}@@"
        html = html.replace(f"<p>{token}</p>", block)
        html = html.replace(token, block)
    return mark_safe(html)


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

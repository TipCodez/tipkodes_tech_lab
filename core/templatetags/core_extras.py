from urllib.parse import urlencode, urlparse
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

    def is_safe_absolute_url(raw_url):
        parsed = urlparse(raw_url)
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc)

    def is_safe_media_url(raw_url):
        return is_safe_absolute_url(raw_url) or (raw_url.startswith("/") and not raw_url.startswith("//"))

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

    def parse_embed_lines(body):
        data = {}
        plain_lines = []
        for raw_line in body.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            key, separator, value = line.partition(":")
            normalized_key = key.strip().lower()
            if separator and normalized_key in {"url", "title", "description", "label", "alt", "caption", "size"}:
                data[normalized_key] = value.strip()
            else:
                plain_lines.append(line)
        if plain_lines:
            data.setdefault("url", plain_lines[0])
        if len(plain_lines) > 1:
            data.setdefault("title", plain_lines[1])
        if len(plain_lines) > 2:
            data.setdefault("description", " ".join(plain_lines[2:]))
        return data

    def stash_link(match):
        data = parse_embed_lines(match.group(1).strip())
        raw_url = data.get("url", "")
        if not is_safe_absolute_url(raw_url):
            return ""
        title = data.get("title") or urlparse(raw_url).netloc
        description = data.get("description") or raw_url
        label = data.get("label") or "Open resource"
        token = f"@@SPECIAL_BLOCK_{len(special_blocks)}@@"
        special_blocks.append(
            f'<a class="blog-link-embed" href="{escape(raw_url)}" target="_blank" rel="noopener noreferrer">'
            '<span class="blog-link-embed-icon"><i class="bi bi-link-45deg"></i></span>'
            '<span class="blog-link-embed-copy">'
            f'<strong>{escape(title)}</strong>'
            f'<small>{escape(description)}</small>'
            '</span>'
            f'<span class="blog-link-embed-action">{escape(label)} <i class="bi bi-box-arrow-up-right"></i></span>'
            '</a>'
        )
        return token

    without_code = re.sub(r":::[ \t]*link[ \t]*(?:\r?\n)(.*?)(?:\r?\n)?:::", stash_link, without_code, flags=re.DOTALL | re.IGNORECASE)

    def stash_image(match):
        data = parse_embed_lines(match.group(1).strip())
        raw_url = data.get("url", "")
        if not is_safe_media_url(raw_url):
            return ""
        caption = data.get("caption") or data.get("title") or ""
        alt = data.get("alt") or caption or "Blog image"
        size = (data.get("size") or "wide").lower()
        size_class = "is-compact" if size == "compact" else "is-full" if size == "full" else "is-wide"
        caption_html = f'<figcaption>{escape(caption)}</figcaption>' if caption else ""
        token = f"@@SPECIAL_BLOCK_{len(special_blocks)}@@"
        special_blocks.append(
            f'<figure class="blog-content-image {size_class}">'
            f'<img src="{escape(raw_url)}" alt="{escape(alt)}">'
            f"{caption_html}"
            '</figure>'
        )
        return token

    without_code = re.sub(r":::[ \t]*image[ \t]*(?:\r?\n)(.*?)(?:\r?\n)?:::", stash_image, without_code, flags=re.DOTALL | re.IGNORECASE)

    def stash_heading(match):
        marks = match.group(1)
        title = match.group(2).strip()
        level = min(max(len(marks), 2), 4)
        token = f"@@SPECIAL_BLOCK_{len(special_blocks)}@@"
        classes = {
            2: "blog-section-heading",
            3: "blog-subsection-heading",
            4: "blog-note-heading",
        }
        icons = {
            2: "bi-bookmark-star",
            3: "bi-chevron-right",
            4: "bi-dot",
        }
        special_blocks.append(
            f'<h{level} class="{classes[level]}">'
            f'<i class="bi {icons[level]}"></i>'
            f'<span>{escape(title)}</span>'
            f'</h{level}>'
        )
        return token

    without_code = re.sub(r"(?m)^[ \t]*(#{1,4})[ \t]+(.+?)[ \t]*$", stash_heading, without_code)

    def split_table_row(row):
        cleaned = row.strip()
        if cleaned.startswith("|"):
            cleaned = cleaned[1:]
        if cleaned.endswith("|"):
            cleaned = cleaned[:-1]
        return [cell.strip() for cell in cleaned.split("|")]

    def is_table_separator(row):
        cells = split_table_row(row)
        return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")) for cell in cells)

    def stash_tables(content):
        lines = content.splitlines()
        rendered = []
        index = 0
        while index < len(lines):
            line = lines[index]
            if "|" not in line or index + 1 >= len(lines) or not is_table_separator(lines[index + 1]):
                rendered.append(line)
                index += 1
                continue

            header = split_table_row(line)
            rows = []
            index += 2
            while index < len(lines) and "|" in lines[index] and lines[index].strip():
                rows.append(split_table_row(lines[index]))
                index += 1

            token = f"@@SPECIAL_BLOCK_{len(special_blocks)}@@"
            head_html = "".join(f"<th>{escape(cell)}</th>" for cell in header)
            body_rows = []
            for row in rows:
                normalized = row + [""] * (len(header) - len(row))
                cells = "".join(f"<td>{escape(cell)}</td>" for cell in normalized[: len(header)])
                body_rows.append(f"<tr>{cells}</tr>")
            special_blocks.append(
                '<div class="blog-table-wrap">'
                '<table class="blog-custom-table">'
                f"<thead><tr>{head_html}</tr></thead>"
                f"<tbody>{''.join(body_rows)}</tbody>"
                '</table>'
                '</div>'
            )
            rendered.append(token)
        return "\n".join(rendered)

    without_code = stash_tables(without_code)

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

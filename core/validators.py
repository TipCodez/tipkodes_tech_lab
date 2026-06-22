from pathlib import Path

from django.core.exceptions import ValidationError


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
PDF_EXTENSIONS = {".pdf"}


def validate_image_file(value):
    ext = Path(value.name).suffix.lower()
    if ext not in IMAGE_EXTENSIONS:
        raise ValidationError("Upload a JPG, JPEG, PNG, or WEBP image.")


def validate_pdf_file(value):
    ext = Path(value.name).suffix.lower()
    if ext not in PDF_EXTENSIONS:
        raise ValidationError("Upload a PDF document.")

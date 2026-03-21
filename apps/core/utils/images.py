from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile


def optimize_image(image_field, max_size=(1600, 1600), quality=85):
    """
    Resize and optimize uploaded images.
    Keeps original format when possible.
    """
    if not image_field:
        return

    image_field.open()
    img = Image.open(image_field)
    img_format = img.format or "JPEG"

    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    img.thumbnail(max_size, Image.LANCZOS)

    buffer = BytesIO()
    save_kwargs = {"optimize": True}
    if img_format.upper() in {"JPEG", "JPG"}:
        save_kwargs["quality"] = quality
    img.save(buffer, format=img_format, **save_kwargs)

    image_field.save(image_field.name, ContentFile(buffer.getvalue()), save=False)
    image_field.close()

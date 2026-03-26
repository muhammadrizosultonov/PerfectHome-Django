from modeltranslation.translator import TranslationOptions, register

from .models import Brand


@register(Brand)
class BrandTranslationOptions(TranslationOptions):
    fields = ("name", "description")

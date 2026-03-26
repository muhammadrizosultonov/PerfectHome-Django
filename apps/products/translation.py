from modeltranslation.translator import TranslationOptions, register

from .models import Product, ProductImage, ProductTag


@register(ProductTag)
class ProductTagTranslationOptions(TranslationOptions):
    fields = ("name",)


@register(Product)
class ProductTranslationOptions(TranslationOptions):
    fields = ("name", "description", "country_of_origin")


@register(ProductImage)
class ProductImageTranslationOptions(TranslationOptions):
    fields = ("alt_text",)

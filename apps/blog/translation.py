from modeltranslation.translator import TranslationOptions, register

from .models import BlogPost


@register(BlogPost)
class BlogPostTranslationOptions(TranslationOptions):
    fields = ("title", "content")

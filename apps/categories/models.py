from django.db import models
from django.urls import reverse
from django.utils.text import slugify


def _unique_slug(instance, base, slug_field="slug"):
    slug = slugify(base) or "item"
    unique = slug
    suffix = 2
    Model = instance.__class__
    while Model.objects.filter(**{slug_field: unique}).exclude(pk=instance.pk).exists():
        unique = f"{slug}-{suffix}"
        suffix += 1
    return unique


class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self):
        return reverse("products:catalog") + f"?category={self.id}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = _unique_slug(self, self.name)
        super().save(*args, **kwargs)

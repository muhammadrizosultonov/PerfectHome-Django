from django.db import models
from django.urls import reverse
from django.utils.text import slugify


def _unique_slug(instance, base, slug_field="slug", allow_unicode=False):
    slug = slugify(base, allow_unicode=allow_unicode) or "item"
    unique = slug
    suffix = 2
    Model = instance.__class__
    while Model.objects.filter(**{slug_field: unique}).exclude(pk=instance.pk).exists():
        unique = f"{slug}-{suffix}"
        suffix += 1
    return unique


class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, allow_unicode=False)
    image = models.ImageField(upload_to="categories/images/", blank=True, null=True)
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
            self.slug = _unique_slug(self, self.name, allow_unicode=False)
        if self.image:
            from apps.core.utils.images import optimize_image

            optimize_image(self.image)
        super().save(*args, **kwargs)

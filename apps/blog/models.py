from django.db import models
from django.urls import reverse
from django.utils.text import slugify


def _unique_slug(instance, base, slug_field="slug"):
    slug = slugify(base, allow_unicode=True) or "item"
    unique = slug
    suffix = 2
    Model = instance.__class__
    while Model.objects.filter(**{slug_field: unique}).exclude(pk=instance.pk).exists():
        unique = f"{slug}-{suffix}"
        suffix += 1
    return unique


class BlogPost(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, allow_unicode=True)
    content = models.TextField()
    cover_image = models.ImageField(upload_to="blog/covers/")
    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        verbose_name = "Blog Post"
        verbose_name_plural = "Blog Posts"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self):
        return reverse("blog:detail", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = _unique_slug(self, self.title)
        if self.cover_image:
            from apps.core.utils.images import optimize_image

            optimize_image(self.cover_image)
        super().save(*args, **kwargs)

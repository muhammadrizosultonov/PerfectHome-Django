from django.db import models
from django.urls import reverse


class Brand(models.Model):
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to="brands/logos/")
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = "Brand"
        verbose_name_plural = "Brands"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self):
        return reverse("products:catalog") + f"?brand={self.id}"

    def save(self, *args, **kwargs):
        if self.logo:
            from apps.core.utils.images import optimize_image

            optimize_image(self.logo)
        super().save(*args, **kwargs)

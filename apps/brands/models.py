from django.db import models
from django.urls import reverse


class Brand(models.Model):
    name = models.CharField(max_length=255)
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
        super().save(*args, **kwargs)

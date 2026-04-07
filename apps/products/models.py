from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.db.models import QuerySet


def _unique_slug(instance, base, slug_field="slug", allow_unicode=False):
    slug = slugify(base, allow_unicode=allow_unicode) or "item"
    unique = slug
    suffix = 2
    Model = instance.__class__
    while Model.objects.filter(**{slug_field: unique}).exclude(pk=instance.pk).exists():
        unique = f"{slug}-{suffix}"
        suffix += 1
    return unique


class ProductTag(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True, allow_unicode=True)

    class Meta:
        verbose_name = "Product Tag"
        verbose_name_plural = "Product Tags"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = _unique_slug(self, self.name, allow_unicode=True)
        super().save(*args, **kwargs)


class ProductQuerySet(QuerySet):
    def with_related(self):
        return self.select_related("brand", "category").prefetch_related("tags", "images")


class Product(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, allow_unicode=True)
    description = models.TextField()
    category = models.ForeignKey(
        "categories.Category",
        on_delete=models.PROTECT,
        related_name="products",
    )
    brand = models.ForeignKey(
        "brands.Brand",
        on_delete=models.PROTECT,
        related_name="products",
    )
    country_of_origin = models.CharField(max_length=120, db_index=True)
    article_number = models.CharField(max_length=120, db_index=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    tags = models.ManyToManyField(ProductTag, blank=True, related_name="products")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ProductQuerySet.as_manager()
    
    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["country_of_origin"]),
            models.Index(fields=["article_number"]),
        ]

    
    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self):
        return reverse("products:detail", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = _unique_slug(self, self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    @property
    def primary_image(self):
        return self.images.first()


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="products/images/")
    alt_text = models.CharField(max_length=255, blank=True)


    class Meta:
        verbose_name = "Product Image"
        verbose_name_plural = "Product Images"
        ordering = ["id"]

    def __str__(self) -> str:
        return f"{self.product.name} Image"

    def save(self, *args, **kwargs):
        if self.image:
            from apps.core.utils.images import optimize_image

            optimize_image(self.image)
        super().save(*args, **kwargs)

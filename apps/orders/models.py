from django.db import models


class OrderRequest(models.Model):
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE, related_name="order_requests")
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=50)
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Order Request"
        verbose_name_plural = "Order Requests"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.name} - {self.product.name}"

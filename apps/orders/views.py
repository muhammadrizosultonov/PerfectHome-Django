from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect

from apps.products.models import Product
from .forms import OrderRequestForm


def order_request_create(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug)
    is_async = request.headers.get("HX-Request") or request.headers.get("X-Requested-With") == "XMLHttpRequest"

    if request.method == "POST":
        form = OrderRequestForm(request.POST)
        if form.is_valid():
            order_request = form.save(commit=False)
            order_request.product = product
            order_request.save()

            if is_async:
                return JsonResponse({"ok": True, "message": "Request sent."})

            messages.success(request, "Request sent. We will contact you shortly.")
            return redirect(product.get_absolute_url())

        if is_async:
            error_text = "Invalid request."
            if "phone" in form.errors:
                error_text = "Telefon raqami noto‘g‘ri formatda."
            return JsonResponse({"ok": False, "error": error_text}, status=400)

    return redirect(product.get_absolute_url())

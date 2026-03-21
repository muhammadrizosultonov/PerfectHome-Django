from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect

from apps.products.models import Product
from .forms import OrderRequestForm


def order_request_create(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug)

    if request.method == "POST":
        form = OrderRequestForm(request.POST)
        if form.is_valid():
            order_request = form.save(commit=False)
            order_request.product = product
            order_request.save()

            if request.headers.get("HX-Request"):
                response = HttpResponse("<div class='text-stone'>Request sent.</div>")
                response["HX-Trigger"] = "order-success"
                return response

            messages.success(request, "Request sent. We will contact you shortly.")
            return redirect(product.get_absolute_url())

        if request.headers.get("HX-Request"):
            return HttpResponse("<div class='text-stone'>Invalid request.</div>", status=400)

    return redirect(product.get_absolute_url())

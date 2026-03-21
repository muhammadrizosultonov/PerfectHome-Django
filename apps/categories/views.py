from django.db.models import Count, Q
from django.shortcuts import render

from .models import Category


def category_list(request):
    query = request.GET.get("q", "").strip()
    has_products = request.GET.get("has_products")

    categories = Category.objects.all().annotate(product_count=Count("products", distinct=True))
    if query:
        categories = categories.filter(Q(name__icontains=query) | Q(description__icontains=query))

    if has_products == "1":
        categories = categories.filter(product_count__gt=0)

    context = {
        "categories": categories,
        "query": query,
        "has_products": has_products,
    }
    return render(request, "categories.html", context)

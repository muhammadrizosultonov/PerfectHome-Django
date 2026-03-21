from django.db.models import Count, Q
from django.shortcuts import render

from .models import Brand


SORT_MAP = {
    "name": "name",
    "-name": "-name",
    "products": "product_count",
    "-products": "-product_count",
}


def brand_list(request):
    query = request.GET.get("q", "").strip()
    sort = request.GET.get("sort", "name")

    brands = Brand.objects.all().annotate(product_count=Count("products", distinct=True))
    if query:
        brands = brands.filter(Q(name__icontains=query) | Q(description__icontains=query))

    ordering = SORT_MAP.get(sort, "name")
    brands = brands.order_by(ordering)

    context = {
        "brands": brands,
        "featured_brands": brands[:2],
        "query": query,
        "sort": sort,
    }
    return render(request, "brands.html", context)

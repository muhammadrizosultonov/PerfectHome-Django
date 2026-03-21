from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, render

from apps.brands.models import Brand
from apps.categories.models import Category
from .models import Product, ProductTag
from apps.orders.forms import OrderRequestForm


PRODUCTS_PER_PAGE = 12


def _build_querystring(request, exclude_keys=None):
    params = request.GET.copy()
    exclude_keys = exclude_keys or []
    for key in exclude_keys:
        params.pop(key, None)
    return params.urlencode()


def product_catalog(request):
    query = request.GET.get("q", "").strip()
    category_values = request.GET.getlist("category")
    brand_values = request.GET.getlist("brand")
    country_values = request.GET.getlist("country")
    tag_slug = request.GET.get("tag")
    sort = request.GET.get("sort")

    products = Product.objects.with_related().all()

    if query:
        products = products.filter(
            Q(name__icontains=query)
            | Q(description__icontains=query)
            | Q(article_number__icontains=query)
        )
    if category_values:
        if all(value.isdigit() for value in category_values):
            products = products.filter(category_id__in=category_values)
        else:
            products = products.filter(category__slug__in=category_values)
    if brand_values:
        products = products.filter(brand_id__in=brand_values)
    if country_values:
        products = products.filter(country_of_origin__in=country_values)
    if tag_slug:
        products = products.filter(tags__slug=tag_slug)

    if sort == "name":
        products = products.order_by("name")
    elif sort == "-name":
        products = products.order_by("-name")
    elif sort == "newest":
        products = products.order_by("-created_at")

    paginator = Paginator(products, PRODUCTS_PER_PAGE)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.annotate(product_count=Count("products", distinct=True)).all()
    brands = Brand.objects.all()
    tags = ProductTag.objects.all()
    countries = (
        Product.objects.values_list("country_of_origin", flat=True)
        .order_by("country_of_origin")
        .distinct()
    )

    context = {
        "products": page_obj,
        "categories": categories,
        "filter_brands": brands,
        "tags": tags,
        "countries": countries,
        "query": query,
        "selected_categories": category_values,
        "selected_brands": brand_values,
        "selected_countries": country_values,
        "selected_tag": tag_slug,
        "sort": sort,
    }
    return render(request, "products.html", context)


def product_detail(request, slug):
    product = get_object_or_404(Product.objects.with_related(), slug=slug)
    order_form = OrderRequestForm()
    related_products = (
        Product.objects.with_related()
        .filter(category=product.category)
        .exclude(id=product.id)
        .order_by("-created_at")[:4]
    )

    context = {
        "product": product,
        "order_form": order_form,
        "related_products": related_products,
    }
    return render(request, "product_detail.html", context)

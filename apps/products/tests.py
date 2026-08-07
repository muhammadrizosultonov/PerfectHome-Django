from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from apps.brands.models import Brand
from apps.categories.models import Category

from .models import Product


class ProductCatalogTests(TestCase):
    def setUp(self):
        self.brand = Brand.objects.create(name="Catalog brand")
        self.category = Category.objects.create(name="Catalog category", slug="catalog-category")
        for number in range(13):
            Product.objects.create(
                name=f"Product {number:02d}",
                slug=f"product-{number:02d}",
                description="Catalog test product",
                category=self.category,
                brand=self.brand,
                country_of_origin="Uzbekistan",
                article_number=f"ART-{number:02d}",
                price=Decimal("100.00"),
            )

    def test_catalog_exposes_next_page_url_that_keeps_active_filters(self):
        response = self.client.get(
            reverse("products:catalog"),
            {"brand": self.brand.pk, "sort": "name"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="load-more"')
        self.assertContains(
            response,
            f"data-next-url=\"?brand={self.brand.pk}&amp;sort=name&amp;page=2\"",
        )

    def test_catalog_sorts_products_by_name(self):
        response = self.client.get(reverse("products:catalog"), {"sort": "name"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["products"][0].name, "Product 00")

    def test_catalog_splits_large_pagination_into_rows_of_fifteen(self):
        Product.objects.bulk_create(
            [
                Product(
                    name=f"Extra product {number:03d}",
                    slug=f"extra-product-{number:03d}",
                    description="Pagination test product",
                    category=self.category,
                    brand=self.brand,
                    country_of_origin="Uzbekistan",
                    article_number=f"EXTRA-{number:03d}",
                    price=Decimal("100.00"),
                )
                for number in range(168)
            ]
        )

        response = self.client.get(reverse("products:catalog"))

        self.assertEqual(len(response.context["pagination_rows"]), 2)
        self.assertEqual(response.context["pagination_rows"][0], list(range(1, 16)))
        self.assertEqual(response.context["pagination_rows"][1], [16])

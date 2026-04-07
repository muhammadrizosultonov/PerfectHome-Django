from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.brands.models import Brand
from apps.categories.models import Category
from apps.products.models import Product, ProductTag


User = get_user_model()


class AdminAuthFlowTests(TestCase):
    def setUp(self):
        self.staff_user = User.objects.create_user(
            username="staff",
            password="secret123",
            is_staff=True,
        )
        self.regular_user = User.objects.create_user(
            username="regular",
            password="secret123",
        )

    def test_admin_dashboard_redirects_anonymous_user_to_login_with_next(self):
        admin_url = reverse("users:admin_dashboard")
        response = self.client.get(admin_url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            f"{reverse('users:login')}?next={admin_url}",
        )

    def test_staff_login_redirects_to_next_url(self):
        next_url = reverse("users:admin_dashboard")
        response = self.client.post(
            reverse("users:login"),
            {
                "username": "staff",
                "password": "secret123",
                "next": next_url,
            },
        )

        self.assertRedirects(response, next_url)

    def test_non_staff_user_cannot_login_to_admin_panel(self):
        response = self.client.post(
            reverse("users:login"),
            {
                "username": "regular",
                "password": "secret123",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Доступ только для сотрудников")
        self.assertNotIn("_auth_user_id", self.client.session)


class AdminProductUpdateTests(TestCase):
    def setUp(self):
        self.staff_user = User.objects.create_user(
            username="staff",
            password="secret123",
            is_staff=True,
        )
        self.client.force_login(self.staff_user)

        self.category = Category.objects.create(name="Kitchen", slug="kitchen")
        self.brand = Brand.objects.create(name="Grohe")
        self.tag = ProductTag.objects.create(name="Featured", slug="featured")
        self.other_product = Product.objects.create(
            name="Other Product",
            slug="other-product",
            description="Other",
            category=self.category,
            brand=self.brand,
            country_of_origin="Germany",
            article_number="ART-002",
            price=Decimal("250000"),
        )
        self.product = Product.objects.create(
            name="Old Product",
            slug="old-product",
            description="Old description",
            category=self.category,
            brand=self.brand,
            country_of_origin="Italy",
            article_number="ART-001",
            price=Decimal("100000"),
        )

    def test_product_update_saves_valid_changes(self):
        response = self.client.post(
            reverse("users:admin_product_edit", args=[self.product.pk]),
            {
                "name": "Updated Product",
                "slug": "updated-product",
                "description": "Updated description",
                "category": self.category.pk,
                "brand": self.brand.pk,
                "country_of_origin": "Spain",
                "article_number": "ART-001-NEW",
                "price": "150000",
                "name_uz": "Yangilangan mahsulot",
                "description_uz": "Yangilangan tavsif",
                "country_of_origin_uz": "Ispaniya",
                "tags": [self.tag.pk],
            },
        )

        self.assertRedirects(response, reverse("users:admin_product_list"))
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, "Updated Product")
        self.assertEqual(self.product.slug, "updated-product")
        self.assertEqual(self.product.article_number, "ART-001-NEW")
        self.assertEqual(self.product.price, Decimal("150000"))
        self.assertEqual(self.product.name_uz, "Yangilangan mahsulot")
        self.assertEqual(list(self.product.tags.values_list("pk", flat=True)), [self.tag.pk])

    def test_product_update_keeps_existing_data_on_validation_error(self):
        response = self.client.post(
            reverse("users:admin_product_edit", args=[self.product.pk]),
            {
                "name": "Broken Product",
                "slug": self.other_product.slug,
                "description": "Broken description",
                "category": self.category.pk,
                "brand": self.brand.pk,
                "country_of_origin": "Spain",
                "article_number": "ART-001-NEW",
                "price": "150000",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Slug")
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, "Old Product")
        self.assertEqual(self.product.slug, "old-product")


class AdminProductUnicodeSlugTests(TestCase):
    def setUp(self):
        self.staff_user = User.objects.create_user(
            username="staff-unicode",
            password="secret123",
            is_staff=True,
        )
        self.client.force_login(self.staff_user)
        self.category = Category.objects.create(name="Bathroom", slug="bathroom")
        self.brand = Brand.objects.create(name="Grohe")

    def test_product_create_accepts_cyrillic_slug(self):
        response = self.client.post(
            reverse("users:admin_product_create"),
            {
                "name": "Смеситель для ванны",
                "slug": "смеситель-для-ванны",
                "description": "Описание",
                "category": self.category.pk,
                "brand": self.brand.pk,
                "country_of_origin": "Россия",
                "article_number": "RU-001",
                "price": "120000",
            },
        )

        self.assertRedirects(response, reverse("users:admin_product_list"))
        product = Product.objects.get(article_number="RU-001")
        self.assertEqual(product.slug, "смеситель-для-ванны")

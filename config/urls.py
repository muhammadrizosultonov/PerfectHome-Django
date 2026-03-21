from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n")),
]

urlpatterns += i18n_patterns(
    path("admin/", admin.site.urls),
    path("", include("apps.core.urls")),
    path("brands/", include("apps.brands.urls")),
    path("categories/", include("apps.categories.urls")),
    path("products/", include("apps.products.urls")),
    path("blog/", include("apps.blog.urls")),
    path("orders/", include("apps.orders.urls")),
    path("auth/", include("apps.users.urls")),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

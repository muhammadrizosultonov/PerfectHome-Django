from django.urls import path
from . import views

app_name = "products"

urlpatterns = [
    path("", views.product_catalog, name="catalog"),
    path("<str:slug>/", views.product_detail, name="detail"),
]

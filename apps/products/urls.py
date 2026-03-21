from django.urls import path
from . import views

app_name = "products"

urlpatterns = [
    path('products/<str:slug>/', views.product_detail, name='detail'),
    path("", views.product_catalog, name="catalog"),
    path("<slug:slug>/", views.product_detail, name="detail"),
]

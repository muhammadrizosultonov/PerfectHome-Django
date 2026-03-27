from django.urls import path
from . import views

app_name = "orders"

urlpatterns = [
    path("request/<str:product_slug>/", views.order_request_create, name="request_create"),
]

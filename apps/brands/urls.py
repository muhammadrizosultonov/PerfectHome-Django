from django.urls import path
from . import views

app_name = "brands"

urlpatterns = [
    path("", views.brand_list, name="list"),
]

from django.forms import ModelForm
from apps.products.models import Product
from apps.categories.models import Category
from apps.brands.models import Brand
from apps.blog.models import BlogPost


class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = "__all__"


class CategoryForm(ModelForm):
    class Meta:
        model = Category
        fields = "__all__"


class BrandForm(ModelForm):
    class Meta:
        model = Brand
        fields = "__all__"


class BlogForm(ModelForm):
    class Meta:
        model = BlogPost
        fields = "__all__"
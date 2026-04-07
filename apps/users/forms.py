from django import forms
from django.contrib.auth import authenticate
from django.forms import ModelForm

from apps.blog.models import BlogPost
from apps.brands.models import Brand
from apps.categories.models import Category
from apps.products.models import Product, ProductImage, ProductTag


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    widget = MultipleFileInput

    def clean(self, data, initial=None):
        single_file_clean = super().clean

        if not data:
            return []
        if isinstance(data, (list, tuple)):
            return [single_file_clean(item, initial) for item in data]
        return [single_file_clean(data, initial)]


class AdminLoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

    error_messages = {
        "invalid_login": "Неверное имя пользователя или пароль",
        "not_staff": "Доступ только для сотрудников (staff)",
    }

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")

        if not username or not password:
            return cleaned_data

        self.user_cache = authenticate(self.request, username=username, password=password)
        if self.user_cache is None:
            raise forms.ValidationError(self.error_messages["invalid_login"])
        if not (self.user_cache.is_staff or self.user_cache.is_superuser):
            raise forms.ValidationError(self.error_messages["not_staff"])

        return cleaned_data

    def get_user(self):
        return self.user_cache


class AdminProductForm(forms.ModelForm):
    slug = forms.SlugField(required=False, allow_unicode=True)
    name_uz = forms.CharField(required=False)
    description_uz = forms.CharField(required=False, widget=forms.Textarea)
    country_of_origin_uz = forms.CharField(required=False)
    tags = forms.ModelMultipleChoiceField(
        queryset=ProductTag.objects.none(),
        required=False,
    )
    images = MultipleFileField(
        required=False,
        widget=MultipleFileInput(attrs={"multiple": True, "accept": "image/*"}),
    )

    class Meta:
        model = Product
        fields = [
            "name",
            "slug",
            "description",
            "category",
            "brand",
            "country_of_origin",
            "article_number",
            "price",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["tags"].queryset = ProductTag.objects.order_by("name")
        self.fields["price"].localize = False
        self.fields["price"].widget.attrs.update({"step": "0.01", "min": "0"})

        if self.instance.pk:
            self.fields["tags"].initial = self.instance.tags.values_list("pk", flat=True)
            self.fields["name_uz"].initial = getattr(self.instance, "name_uz", "")
            self.fields["description_uz"].initial = getattr(self.instance, "description_uz", "")
            self.fields["country_of_origin_uz"].initial = getattr(self.instance, "country_of_origin_uz", "")

    def save(self, commit=True):
        product = super().save(commit=False)
        product.name_uz = self.cleaned_data.get("name_uz", "").strip()
        product.description_uz = self.cleaned_data.get("description_uz", "").strip()
        product.country_of_origin_uz = self.cleaned_data.get("country_of_origin_uz", "").strip()

        if not commit:
            return product

        product.save()
        product.tags.set(self.cleaned_data.get("tags") or [])

        for image in self.cleaned_data.get("images", []):
            ProductImage.objects.create(
                product=product,
                image=image,
                alt_text=product.name,
            )

        return product


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

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.views import redirect_to_login
from django.db import transaction
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from django.views import View

from apps.blog.models import BlogPost
from apps.brands.models import Brand
from apps.categories.models import Category
from apps.orders.models import OrderRequest
from apps.products.models import Product, ProductImage, ProductTag

from .forms import AdminLoginForm, AdminProductForm


def _get_safe_next_url(request):
    next_url = request.POST.get("next") or request.GET.get("next")
    if next_url and url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return next_url
    return ""


def _get_post_login_redirect(request, user):
    if not (user.is_staff or user.is_superuser):
        return reverse("core:home")
    next_url = _get_safe_next_url(request)
    if next_url:
        return next_url
    return reverse("users:admin_dashboard")


def _build_admin_product_context(form):
    return {
        "form": form,
        "product": form.instance,
        "categories": Category.objects.order_by("name"),
        "brands": Brand.objects.order_by("name"),
        "tags": ProductTag.objects.order_by("name"),
        "selected_tags": {str(tag_id) for tag_id in (form["tags"].value() or [])},
    }

class StaffRequiredMixin(UserPassesTestMixin):
    login_url = "users:login"
    redirect_field_name = "next"

    def test_func(self):
        return self.request.user.is_authenticated and (self.request.user.is_staff or self.request.user.is_superuser)

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect_to_login(
                self.request.get_full_path(),
                reverse(self.login_url),
                self.redirect_field_name,
            )
        messages.error(self.request, "У вас нет доступа к административной панели")
        return redirect('core:home')


def user_login(request):
    if request.user.is_authenticated:
        return redirect(_get_post_login_redirect(request, request.user))

    if request.method == "POST":
        form = AdminLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"С возвращением, {user.username}!")
            return redirect(_get_post_login_redirect(request, user))
    else:
        form = AdminLoginForm(request)

    return render(
        request,
        "auth/login.html",
        {
            "form": form,
            "next": _get_safe_next_url(request),
        },
    )


@require_POST
def user_logout(request):
    logout(request)
    return redirect("users:login")

class AdminDashboardView(StaffRequiredMixin, View):
    def get(self, request):
        context = {
            'products_count': Product.objects.count(),
            'categories_count': Category.objects.count(),
            'brands_count': Brand.objects.count(),
            'blog_count': BlogPost.objects.count(),
            'orders_count': OrderRequest.objects.count(),
            'recent_products': Product.objects.all().order_by('-created_at')[:5],
            'recent_orders': OrderRequest.objects.all().order_by('-created_at')[:5],
            'low_stock_products': Product.objects.filter(stock__lt=10)[:5] if hasattr(Product, 'stock') else [],
        }
        return render(request, 'admin_panel/dashboard.html', context)


class AdminProductListView(StaffRequiredMixin, View):
    def get(self, request):
        products = Product.objects.all().select_related('category', 'brand').prefetch_related('images')

        # Фильтрация
        category = request.GET.get('category')
        brand = request.GET.get('brand')
        search = request.GET.get('search')

        if category:
            products = products.filter(category_id=category)
        if brand:
            products = products.filter(brand_id=brand)
        if search:
            products = products.filter(
                Q(name__icontains=search) |
                Q(article_number__icontains=search) |
                Q(description__icontains=search)
            )

        context = {
            'products': products,
            'categories': Category.objects.all(),
            'brands': Brand.objects.all(),
        }
        return render(request, 'admin_panel/products.html', context)


class AdminProductCreateView(StaffRequiredMixin, View):
    def get(self, request):
        form = AdminProductForm()
        return render(request, 'admin_panel/product_create.html', _build_admin_product_context(form))

    def post(self, request):
        form = AdminProductForm(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():
                product = form.save()
            messages.success(request, f'Товар "{product.name}" успешно создан')
            return redirect('users:admin_product_list')

        messages.error(request, 'Проверьте форму и исправьте ошибки')
        return render(request, 'admin_panel/product_create.html', _build_admin_product_context(form))


class AdminProductUpdateView(StaffRequiredMixin, View):
    def get(self, request, pk):
        product = get_object_or_404(Product.objects.prefetch_related('images', 'tags'), pk=pk)
        form = AdminProductForm(instance=product)
        return render(request, 'admin_panel/product_update.html', _build_admin_product_context(form))

    def post(self, request, pk):
        product = get_object_or_404(Product.objects.prefetch_related('images', 'tags'), pk=pk)
        form = AdminProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            with transaction.atomic():
                product = form.save()
            messages.success(request, f'Товар "{product.name}" успешно обновлен')
            return redirect('users:admin_product_list')

        messages.error(request, 'Проверьте форму и исправьте ошибки')
        return render(request, 'admin_panel/product_update.html', _build_admin_product_context(form))


class AdminProductDeleteView(StaffRequiredMixin, View):
    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        product_name = product.name
        product.delete()
        messages.success(request, f'Товар "{product_name}" удален')
        return redirect('users:admin_product_list')


class AdminProductImageDeleteView(StaffRequiredMixin, View):
    def post(self, request, pk):
        image = get_object_or_404(ProductImage, pk=pk)
        product_id = image.product.id
        image.delete()
        messages.success(request, 'Изображение удалено')
        return redirect('users:admin_product_edit', pk=product_id)


class AdminCategoryListView(StaffRequiredMixin, View):
    def get(self, request):
        categories = Category.objects.annotate(
            products_count=Count('products')
        ).all()
        return render(request, 'admin_panel/categories.html', {'categories': categories})


class AdminCategoryCreateView(StaffRequiredMixin, View):
    def get(self, request):
        return render(request, 'admin_panel/category_create.html')

    def post(self, request):
        try:
            category = Category.objects.create(
                name=request.POST.get('name'),
                slug=request.POST.get('slug'),
                description=request.POST.get('description', '')
            )
            name_uz = request.POST.get('name_uz', '').strip()
            description_uz = request.POST.get('description_uz', '').strip()
            image = request.FILES.get('image')
            if name_uz:
                category.name_uz = name_uz
            if description_uz:
                category.description_uz = description_uz
            if image:
                category.image = image
            if name_uz or description_uz or image:
                category.save()
            messages.success(request, f'Категория "{category.name}" создана')
            return redirect('users:admin_category_list')
        except Exception as e:
            messages.error(request, f'Ошибка: {str(e)}')
            return self.get(request)


class AdminCategoryUpdateView(StaffRequiredMixin, View):
    def get(self, request, pk):
        category = get_object_or_404(Category, pk=pk)
        return render(request, 'admin_panel/category_update.html', {'category': category})

    def post(self, request, pk):
        category = get_object_or_404(Category, pk=pk)
        try:
            category.name = request.POST.get('name')
            category.slug = request.POST.get('slug')
            category.description = request.POST.get('description', '')
            category.name_uz = request.POST.get('name_uz', '').strip()
            category.description_uz = request.POST.get('description_uz', '').strip()
            if request.FILES.get('image'):
                category.image = request.FILES['image']
            category.save()
            messages.success(request, 'Категория обновлена')
            return redirect('users:admin_category_list')
        except Exception as e:
            messages.error(request, f'Ошибка: {str(e)}')
            return self.get(request, pk)


class AdminCategoryDeleteView(StaffRequiredMixin, View):
    def post(self, request, pk):
        category = get_object_or_404(Category, pk=pk)
        if category.products.exists():
            messages.error(request, 'Нельзя удалить категорию с товарами')
        else:
            category.delete()
            messages.success(request, 'Категория удалена')
        return redirect('users:admin_category_list')


# ================ BRAND MANAGEMENT ================
class AdminBrandListView(StaffRequiredMixin, View):
    def get(self, request):
        brands = Brand.objects.annotate(
            products_count=Count('products')
        ).all()
        return render(request, 'admin_panel/brands.html', {'brands': brands})


class AdminBrandCreateView(StaffRequiredMixin, View):
    def get(self, request):
        return render(request, 'admin_panel/brand_create.html')

    def post(self, request):
        try:
            brand = Brand.objects.create(
                name=request.POST.get('name'),
                description=request.POST.get('description', '')
            )
            name_uz = request.POST.get('name_uz', '').strip()
            description_uz = request.POST.get('description_uz', '').strip()
            if name_uz:
                brand.name_uz = name_uz
            if description_uz:
                brand.description_uz = description_uz
            if name_uz or description_uz:
                brand.save()

            messages.success(request, f'Бренд "{brand.name}" создан')
            return redirect('users:admin_brand_list')
        except Exception as e:
            messages.error(request, f'Ошибка: {str(e)}')
            return self.get(request)


class AdminBrandUpdateView(StaffRequiredMixin, View):
    def get(self, request, pk):
        brand = get_object_or_404(Brand, pk=pk)
        return render(request, 'admin_panel/brand_update.html', {'brand': brand})

    def post(self, request, pk):
        brand = get_object_or_404(Brand, pk=pk)
        try:
            brand.name = request.POST.get('name')
            brand.description = request.POST.get('description', '')
            brand.name_uz = request.POST.get('name_uz', '').strip()
            brand.description_uz = request.POST.get('description_uz', '').strip()

            brand.save()
            messages.success(request, 'Бренд обновлен')
            return redirect('users:admin_brand_list')
        except Exception as e:
            messages.error(request, f'Ошибка: {str(e)}')
            return self.get(request, pk)


class AdminBrandDeleteView(StaffRequiredMixin, View):
    def post(self, request, pk):
        brand = get_object_or_404(Brand, pk=pk)
        if brand.products.exists():
            messages.error(request, 'Нельзя удалить бренд с товарами')
        else:
            brand.delete()
            messages.success(request, 'Бренд удален')
        return redirect('users:admin_brand_list')


# ================ TAG MANAGEMENT ================
class AdminTagListView(StaffRequiredMixin, View):
    def get(self, request):
        tags = ProductTag.objects.annotate(
            products_count=Count('products', distinct=True)
        ).all()
        return render(request, 'admin_panel/tags.html', {'tags': tags})


class AdminTagCreateView(StaffRequiredMixin, View):
    def get(self, request):
        return render(request, 'admin_panel/tag_create.html')

    def post(self, request):
        try:
            name = request.POST.get('name')
            slug = request.POST.get('slug', '')
            tag = ProductTag.objects.create(
                name=name,
                slug=slug,
            )
            name_uz = request.POST.get('name_uz', '').strip()
            if name_uz:
                tag.name_uz = name_uz
                tag.save()
            messages.success(request, f'Тег "{tag.name}" создан')
            return redirect('users:admin_tag_list')
        except Exception as e:
            messages.error(request, f'Ошибка: {str(e)}')
            return self.get(request)


class AdminTagUpdateView(StaffRequiredMixin, View):
    def get(self, request, pk):
        tag = get_object_or_404(ProductTag, pk=pk)
        return render(request, 'admin_panel/tag_update.html', {'tag': tag})

    def post(self, request, pk):
        tag = get_object_or_404(ProductTag, pk=pk)
        try:
            tag.name = request.POST.get('name')
            tag.slug = request.POST.get('slug', '')
            tag.name_uz = request.POST.get('name_uz', '').strip()
            tag.save()
            messages.success(request, 'Тег обновлен')
            return redirect('users:admin_tag_list')
        except Exception as e:
            messages.error(request, f'Ошибка: {str(e)}')
            return self.get(request, pk)


class AdminTagDeleteView(StaffRequiredMixin, View):
    def post(self, request, pk):
        tag = get_object_or_404(ProductTag, pk=pk)
        if tag.products.exists():
            messages.error(request, 'Нельзя удалить тег с товарами')
        else:
            tag.delete()
            messages.success(request, 'Тег удален')
        return redirect('users:admin_tag_list')


# ================ BLOG MANAGEMENT ================
class AdminBlogListView(StaffRequiredMixin, View):
    def get(self, request):
        posts = BlogPost.objects.all()
        return render(request, 'admin_panel/blog.html', {'posts': posts})


class AdminBlogCreateView(StaffRequiredMixin, View):
    def get(self, request):
        return render(request, 'admin_panel/blog_create.html')

    def post(self, request):
        try:
            post = BlogPost.objects.create(
                title=request.POST.get('title'),
                slug=request.POST.get('slug'),
                content=request.POST.get('content'),
            )
            title_uz = request.POST.get('title_uz', '').strip()
            content_uz = request.POST.get('content_uz', '').strip()
            if title_uz:
                post.title_uz = title_uz
            if content_uz:
                post.content_uz = content_uz
            if title_uz or content_uz:
                post.save()

            if request.FILES.get('cover_image'):
                post.cover_image = request.FILES['cover_image']
                post.save()

            messages.success(request, f'Пост "{post.title}" создан')
            return redirect('users:admin_blog_list')
        except Exception as e:
            messages.error(request, f'Ошибка: {str(e)}')
            return self.get(request)


class AdminBlogUpdateView(StaffRequiredMixin, View):
    def get(self, request, pk):
        post = get_object_or_404(BlogPost, pk=pk)
        return render(request, 'admin_panel/blog_update.html', {'post': post})

    def post(self, request, pk):
        post = get_object_or_404(BlogPost, pk=pk)
        try:
            post.title = request.POST.get('title')
            post.slug = request.POST.get('slug')
            post.content = request.POST.get('content')
            post.title_uz = request.POST.get('title_uz', '').strip()
            post.content_uz = request.POST.get('content_uz', '').strip()

            if request.FILES.get('cover_image'):
                post.cover_image = request.FILES['cover_image']

            post.save()
            messages.success(request, 'Пост обновлен')
            return redirect('users:admin_blog_list')
        except Exception as e:
            messages.error(request, f'Ошибка: {str(e)}')
            return self.get(request, pk)


class AdminBlogDeleteView(StaffRequiredMixin, View):
    def post(self, request, pk):
        post = get_object_or_404(BlogPost, pk=pk)
        post.delete()
        messages.success(request, 'Пост удален')
        return redirect('users:admin_blog_list')


# ================ ORDER REQUESTS MANAGEMENT ================
class AdminOrderListView(StaffRequiredMixin, View):
    def get(self, request):
        orders = OrderRequest.objects.all().select_related('product').order_by('-created_at')
        return render(request, 'admin_panel/orders.html', {'orders': orders})



class AdminOrderDeleteView(StaffRequiredMixin, View):
    def post(self, request, pk):
        order = get_object_or_404(OrderRequest, pk=pk)
        order.delete()
        messages.success(request, 'Заявка удалена')
        return redirect('users:admin_order_list')

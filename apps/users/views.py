from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from apps.products.models import Product,ProductImage,ProductTag,ProductQuerySet
from apps.orders.models import OrderRequest
from .forms import ProductForm
from django.shortcuts import get_object_or_404
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse
from django.db.models import Count, Q
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from apps.categories.models import Category
from apps.brands.models import Brand
from apps.blog.models import BlogPost

class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and (self.request.user.is_staff or self.request.user.is_superuser)

    def handle_no_permission(self):
        messages.error(self.request, "У вас нет доступа к административной панели")
        return redirect('core:home')


def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user:
            if not (user.is_staff or user.is_superuser):
                return render(
                    request,
                    "auth/login.html",
                    {"error": "Доступ только для сотрудников (staff)"},
                )

            login(request, user)
            messages.success(request, f"С возвращением, {username}!")

            if user.is_staff:
                return redirect("users:admin_dashboard")

            return redirect("core:home")

        return render(request, "auth/login.html", {"error": "Неверное имя пользователя или пароль"})

    return render(request, "auth/login.html")


def user_logout(request):
    logout(request)
    return redirect("core:home")

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
        context = {
            'categories': Category.objects.all(),
            'brands': Brand.objects.all(),
            'tags': ProductTag.objects.all(),
        }
        return render(request, 'admin_panel/product_create.html', context)

    def post(self, request):
        # Создание товара
        try:
            product = Product.objects.create(
                name=request.POST.get('name'),
                slug=request.POST.get('slug'),
                description=request.POST.get('description'),
                category_id=request.POST.get('category'),
                brand_id=request.POST.get('brand'),
                country_of_origin=request.POST.get('country_of_origin'),
                article_number=request.POST.get('article_number'),
                price=request.POST.get('price'),
            )

            name_uz = request.POST.get('name_uz', '').strip()
            description_uz = request.POST.get('description_uz', '').strip()
            country_uz = request.POST.get('country_of_origin_uz', '').strip()
            if name_uz:
                product.name_uz = name_uz
            if description_uz:
                product.description_uz = description_uz
            if country_uz:
                product.country_of_origin_uz = country_uz
            if name_uz or description_uz or country_uz:
                product.save()

            # Добавление тегов
            tag_ids = request.POST.getlist('tags')
            if tag_ids:
                product.tags.set(tag_ids)

            # Обработка изображений
            images = request.FILES.getlist('images')
            for image in images:
                ProductImage.objects.create(
                    product=product,
                    image=image,
                    alt_text=request.POST.get(f'alt_{image.name}', product.name)
                )

            messages.success(request, f'Товар "{product.name}" успешно создан')
            return redirect('users:admin_product_list')

        except Exception as e:
            messages.error(request, f'Ошибка при создании товара: {str(e)}')
            return self.get(request)


class AdminProductUpdateView(StaffRequiredMixin, View):
    def get(self, request, pk):
        product = get_object_or_404(Product.objects.prefetch_related('images', 'tags'), pk=pk)
        context = {
            'product': product,
            'categories': Category.objects.all(),
            'brands': Brand.objects.all(),
            'tags': ProductTag.objects.all(),
            'selected_tags': product.tags.values_list('id', flat=True),
        }
        return render(request, 'admin_panel/product_update.html', context)

    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        try:
            # Обновление полей
            product.name = request.POST.get('name')
            product.slug = request.POST.get('slug')
            product.description = request.POST.get('description')
            product.category_id = request.POST.get('category')
            product.brand_id = request.POST.get('brand')
            product.country_of_origin = request.POST.get('country_of_origin')
            product.article_number = request.POST.get('article_number')
            product.price = request.POST.get('price')
            product.name_uz = request.POST.get('name_uz', '').strip()
            product.description_uz = request.POST.get('description_uz', '').strip()
            product.country_of_origin_uz = request.POST.get('country_of_origin_uz', '').strip()
            product.save()

            # Обновление тегов
            tag_ids = request.POST.getlist('tags')
            product.tags.set(tag_ids)

            # Добавление новых изображений
            images = request.FILES.getlist('images')
            for image in images:
                ProductImage.objects.create(
                    product=product,
                    image=image,
                    alt_text=request.POST.get(f'alt_{image.name}', product.name)
                )

            messages.success(request, f'Товар "{product.name}" успешно обновлен')
            return redirect('users:admin_product_list')

        except Exception as e:
            messages.error(request, f'Ошибка при обновлении товара: {str(e)}')
            return self.get(request, pk)


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

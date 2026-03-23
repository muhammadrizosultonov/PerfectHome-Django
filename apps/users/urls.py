from django.urls import path
from . import views
app_name="users"

urlpatterns = [
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    # Admin Dashboard
    path('admin-panel/', views.AdminDashboardView.as_view(), name='admin_dashboard'),

    # Product Management
    path('admin-panel/products/', views.AdminProductListView.as_view(), name='admin_product_list'),
    path('admin-panel/products/create/', views.AdminProductCreateView.as_view(), name='admin_product_create'),
    path('admin-panel/products/<int:pk>/edit/', views.AdminProductUpdateView.as_view(), name='admin_product_edit'),
    path('admin-panel/products/<int:pk>/delete/', views.AdminProductDeleteView.as_view(), name='admin_product_delete'),
    path('admin-panel/products/image/<int:pk>/delete/', views.AdminProductImageDeleteView.as_view(),name='admin_product_image_delete'),

    # Category Management
    path('admin-panel/categories/', views.AdminCategoryListView.as_view(), name='admin_category_list'),
    path('admin-panel/categories/create/', views.AdminCategoryCreateView.as_view(), name='admin_category_create'),
    path('admin-panel/categories/<int:pk>/edit/', views.AdminCategoryUpdateView.as_view(), name='admin_category_edit'),
    path('admin-panel/categories/<int:pk>/delete/', views.AdminCategoryDeleteView.as_view(),
         name='admin_category_delete'),

    # Brand Management
    path('admin-panel/brands/', views.AdminBrandListView.as_view(), name='admin_brand_list'),
    path('admin-panel/brands/create/', views.AdminBrandCreateView.as_view(), name='admin_brand_create'),
    path('admin-panel/brands/<int:pk>/edit/', views.AdminBrandUpdateView.as_view(), name='admin_brand_edit'),
    path('admin-panel/brands/<int:pk>/delete/', views.AdminBrandDeleteView.as_view(), name='admin_brand_delete'),

    # Blog Management
    path('admin-panel/blog/', views.AdminBlogListView.as_view(), name='admin_blog_list'),
    path('admin-panel/blog/create/', views.AdminBlogCreateView.as_view(), name='admin_blog_create'),
    path('admin-panel/blog/<int:pk>/edit/', views.AdminBlogUpdateView.as_view(), name='admin_blog_edit'),
    path('admin-panel/blog/<int:pk>/delete/', views.AdminBlogDeleteView.as_view(), name='admin_blog_delete'),

    # Order Requests Management
    path('admin-panel/orders/', views.AdminOrderListView.as_view(), name='admin_order_list'),
    path('admin-panel/orders/<int:pk>/delete/', views.AdminOrderDeleteView.as_view(), name='admin_order_delete'),
]

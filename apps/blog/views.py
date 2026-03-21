from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render

from .models import BlogPost


def blog_list(request):
    posts = BlogPost.objects.all()
    paginator = Paginator(posts, 6)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)
    return render(request, "blog.html", {"posts": page_obj})


def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug)
    return render(request, "blog_detail.html", {"post": post})

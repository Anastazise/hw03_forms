from django.shortcuts import render
from .models import Post, Group
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from .models import Group, Post
from .forms import PostForm

POSTS_PER_PAGE = 10


def index(request):
    post_list = Post.objects.all().order_by('-pub_date')
    paginator = Paginator(post_list, 10) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()[:POSTS_PER_PAGE]
    context = {
        'group': group,
        'posts': posts,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    context = {
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    context = {
    }
    return render(request, 'posts/post_detail.html', context)


def post_create(request):
    """Добавления поста."""

    template = "posts/create_post.html"

    if request.method == "POST":
        form = PostForm(request.POST or None)

        if form.is_valid():
            text = form.cleaned_data["text"]
            group = form.cleaned_data["group"]

            instance = form.save(commit=False)
            instance.author_id = request.user.id
            instance.save()

            user_name = request.user.username

            return redirect("posts:profile", user_name)

        return render(request, template, {"form": form})

    form = PostForm()

    return render(request, template, {"form": form})


def post_edit(request, post_id):
    """Редактирование поста. Доступно только автору."""

    template = "posts/create_post.html"

    post = get_object_or_404(Post, pk=post_id)

    if request.user.id != post.author.id:
        return redirect("posts:post_detail", post.pk)

    if request.method == "POST":
        form = PostForm(request.POST or None, instance=post)
        if form.is_valid():
            form.save()

            user_name = request.user.username
            return redirect("posts:profile", user_name)

        return render(request, template, {"form": form})

    form = PostForm(instance=post)
    context = {
        "form": form,
        "is_edit": True,
    }
    return render(request, template, context)

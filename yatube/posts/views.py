from django.shortcuts import render
from .models import Post, Group
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import Group, Post, User
from .forms import PostForm
from yatube.settings import POSTS_PER_PAGE


def index(request):
    posts = Post.objects.all()
    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'group': group,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    profile = get_object_or_404(User, username=username)
    posts = (
        Post.objects.select_related("author", "group")
        .filter(author=profile).all()
    )
    posts_count = posts.count()
    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'profile': profile,
        'posts_count': posts_count,
        'page_obj': page_obj,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    template = "posts/post_detail.html"
    context = {'post': post}
    return render(request, template, context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', request.user)
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    is_edit = True
    post = get_object_or_404(Post, pk=post_id)
    if post.author == request.user:
        form = PostForm(request.POST or None, instance=post)
        if form.is_valid():
            post = form.save()
            return redirect('posts:post_detail', post.pk)
        return render(request, "posts/create_post.html",
                      {'form': form, "is_edit": is_edit})

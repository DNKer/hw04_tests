""" YaTube Social Community
Copyright (C) 2022 Authors: Dmitry Korepanov, Yandex practikum
License Free
Version: 1.0.4. 2022"""


from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from . import helpers
from .forms import PostForm
from .models import Group, Post, User

QUANTITY_RECORDS: int = 10
POST_TITLE_CHAR: int = 30


def index(request):
    template = 'posts/index.html'
    posts = Post.objects.all()
    page_obj = helpers.pagination(posts, request, QUANTITY_RECORDS)
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    page_obj = helpers.pagination(posts, request, QUANTITY_RECORDS)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    page_obj = helpers.pagination(posts, request, QUANTITY_RECORDS)
    context = {
        'author': author,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, pk=post_id)
    post_title = post.text[:POST_TITLE_CHAR]
    author = post.author
    number_author_posts = author.posts.all().count()
    context = {
        'post': post,
        'post_title': post_title,
        'author': author,
        'post_id': post_id,
        'number_author_posts': number_author_posts,
        'pub_date': post.pub_date,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    form = PostForm(
        request.POST or None,
    )
    if form.is_valid():
        temp_form = form.save(commit=False)
        temp_form.author = request.user
        temp_form.save()
        return redirect(
            'posts:profile', temp_form.author
        )
    return render(request, template, {'form': form})


@login_required
def post_edit(request, post_id):
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id)
    form = PostForm(
        request.POST or None,
        instance=post,
    )
    if form.is_valid():
        post = form.save()
        return redirect('posts:post_detail', post_id)
    context = {
        'form': form,
        'is_edit': True,
        'post': post,
    }
    return render(request, template, context)

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from yatube import settings

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, settings.PAGE_SIZE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        "page_obj": page_obj,
    }
    return render(request, "posts/index.html", context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, settings.PAGE_SIZE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        "group": group,
        "page_obj": page_obj,
    }
    return render(request, "posts/group_list.html", context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    main_user = request.user
    post_list = author.posts.all()
    paginator = Paginator(post_list, settings.PAGE_SIZE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    post_number = post_list.count()
    follow = Follow.objects.filter(author=author.pk)
    following = True if follow else False
    context = {
        "main_user": main_user,
        "page_obj": page_obj,
        "post_number": post_number,
        "author": author,
        "following": following,
    }
    return render(request, "posts/profile.html", context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    user = get_object_or_404(User, username=post.author)
    post_number = user.posts.filter(author=user).count()
    comments = post.comments.all()
    form = CommentForm()
    context = {
        "post": post,
        "post_number": post_number,
        "post_id": post_id,
        "comments": comments,
        "form": form,
    }
    return render(request, "posts/post_detail.html", context)


@login_required
def post_create(request):

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect("posts:profile", username=post.author)

    return render(
        request, "posts/create_post.html",
        {"form": form, "username": request.user}
    )


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        raise Http404

    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect("posts:post_detail", post_id=post_id)

    return render(
        request,
        "posts/create_post.html",
        {"form": form, "username": request.user, "is_edit": True},
    )


@login_required
def add_comment(request, post_id):
    post = Post.objects.get(pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect("posts:post_detail", post_id=post_id)


@login_required
def profile_follow(request, username):
    # Подписаться на автора
    author = get_object_or_404(User, username=username)
    user = request.user
    if author != user and not (Follow.objects.filter(
            user=request.user, author=author).exists()):
        Follow.objects.get_or_create(user=user, author=author)
    return redirect("posts:profile", username=username)


@login_required
def profile_unfollow(request, username):
    # Дизлайк, отписка
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=author).delete()
    return redirect("posts:profile", username=username)


@login_required
def follow_index(request):
    user = request.user
    author = user.follower.values_list("author", flat=True)
    post_list = Post.objects.filter(author__in=author)
    paginator = Paginator(post_list, settings.PAGE_SIZE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        "page_obj": page_obj,
    }
    return render(request, "posts/follow.html", context)

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Count, Q
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from taggit.models import Tag

from .mixins import ObjectViewMixin
from .models import *
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
    View, TemplateView,
)

from .forms import NewCommentForm
from .models import Comment
from account.models import Account


# Create your views here.


class IndexView(ListView):
    template_name = 'blog/home.html'
    paginate_by = 3
    model = Post


    def get_queryset(self):
        return Post.objects.order_by("-timestamp")


    def get_template_names(self):
        if self.request.htmx:
            return 'blog/post_list.html'
        return 'blog/home.html'


    def get_latest(self, category):
        post = Post.objects.filter(featured=True, category=category).last()
        lastest_post = Post.objects.get(id=post.id)
        return lastest_post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        technology = Category.objects.get(title="Technology")
        tech_latest_post = self.get_latest(technology)
        featured_posts = Post.objects.filter(featured=True)[::-1]
        latest_posts = Post.objects.order_by("-timestamp")[::-1]
        category = Category.objects.all()[0:5]
        context['tech_post'] = tech_latest_post
        context['featured_posts'] = featured_posts
        context['most_read_posts'] = Post.most_read_posts
        context['latest_posts'] = latest_posts
        context['categories'] = category
        return context


class PostDetailView(ObjectViewMixin, DetailView):
    model = Post
    template_name = "blog/post_detail.html"
    _comment_form = NewCommentForm()

    def post(self, request, slug):
        self.post = get_object_or_404(Post, slug=slug)

        # List of active comments for this post
        self.comments = self.post.comments.filter(status=True)
        new_comment = None

        if request.method == 'POST':
            comment_form = NewCommentForm(request.POST)
            if comment_form.is_valid():
                user_comment = comment_form.save(commit=False)
                user_comment.post = self.post
                user_comment.user = request.user.accounts
                user_comment.save()

                return HttpResponseRedirect(self.post.get_absolute_url() + '#' + str(user_comment.id))
        else:
            comment_form = NewCommentForm()

    def get(self, request, *args, **kwargs):
        self.main_post = Post.objects.get(slug=kwargs.get('slug'))
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.main_post
        post_tags = post.tags.most_common()[:4]
        post_tags_ids = Post.tags.values_list('id', flat=True)
        similar_posts_tag = Post.objects.filter(tags__in=post_tags_ids).exclude(id=post.id)
        similar_posts = similar_posts_tag.annotate(same_tags=Count('tags')).order_by('-same_tags', '-timestamp')[:6]

        context['similar_posts'] = similar_posts
        context['post_tags'] = post_tags
        context["latest_posts"] = Post.objects.all().order_by("-timestamp")[0:3]
        context["categories"] = Category.objects.all()
        context["comment_form"] = self._comment_form

        comments = Comment.objects.filter(post=post.id, status=True)
        context["comments"] = comments
        return context


def view_post(request, id):
    post = Post.objects.get(id=id)

    context = {'post': post}
    return render(request, 'posts/post_detail.html', context)


def like_post(request, id):
    user_id = request.user
    account = Account.objects.get(user=user_id)
    featured_posts = Post.objects.filter(featured=True)[0:3]
    latest_posts = Post.objects.order_by("-timestamp")[0:3]
    context = {"featured_posts": featured_posts, "latest_posts": latest_posts}
    if request.method == "POST":
        instance = Post.objects.get(id=id)
        if not instance.likes.filter(id=account.id).exists():
            instance.likes.add(account)
            instance.save()

            return render(request, 'blog/like_area.html', context={'post': instance})
        else:
            instance.likes.remove(account)
            instance.save()

            return render(request, 'blog/like_area.html', context={'post': instance})


@login_required
def fav_post(request, id):
    user_id = request.user
    account = Account.objects.get(user=user_id)
    featured_posts = Post.objects.filter(featured=True)[0:3]
    latest_posts = Post.objects.order_by("-timestamp")[0:3]
    context = {"featured_posts": featured_posts, "latest_posts": latest_posts}
    if request.method == "POST":
        instance = Post.objects.get(id=id)
        if not instance.favourites.filter(id=account.id).exists():
            instance.favourites.add(account)
            instance.save()
            return render(request, 'blog/fav_area.html', context={'post': instance})
        else:
            instance.favourites.remove(account)
            instance.save()
            return render(request, 'blog/fav_area.html', context={'post': instance})


@login_required
def favourite_list(request):
    favourite = Post.objects.filter(favourites=request.user.accounts)

    print(favourite)

    return render(request, 'blog/favourite.html', {'favourites': favourite})


def tag_list(request, tag_slug=None):
    posts = Post.objects.all()

    # post tag
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        tag_posts = Post.objects.filter(tags__in=[tag])[::-1]

        return render(request, 'blog/tag_list.html', {'posts': tag_posts, 'tag': tag})


def category_list(request, name=None):
    if name:
        category = Category.objects.get(title=name)
        cat_posts = Post.objects.filter(category=category)[::-1]

        return render(request, 'blog/tag_list.html', {'posts': cat_posts, 'category': category})


def categories(request):
    category = Category.objects.all()

    return render(request, 'blog/categories.html', {'categories': category})


def search_post(request):
    search_text = request.POST.get('search')
    if search_text == "":
        return HttpResponse("No search text found.")
    results = Post.objects.filter(Q(title__icontains=search_text) | Q(content__icontains=search_text)
                                  )
    context = {"results": results}
    return render(request, 'blog/search-result.html', context)


def search_view(request):
    return render(request, 'blog/search.html', )

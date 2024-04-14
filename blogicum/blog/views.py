from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .forms import CreateCommentForm, CreatePostForm
from .models import Category, Comment, Post, User
from .mixins import CommentEditMixin, PostsEditMixin, PostsQuerySetMixin

PAGINATED_BY = 10


class PostDeleteView(PostsEditMixin, LoginRequiredMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('blog:index')
    pk_url_kwarg = 'post_id'

    def delete(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=self.kwargs[self.pk_url_kwarg])
        if self.request.user != post.author:
            return redirect('blog:index')

        return super().delete(request, *args, **kwargs)


class PostUpdateView(PostsEditMixin, LoginRequiredMixin, UpdateView):
    form_class = CreatePostForm
    model = Post
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=self.kwargs[self.pk_url_kwarg])
        if self.request.user != post.author:
            return redirect('blog:post_detail',
                            post_id=self.kwargs[self.pk_url_kwarg])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:post_detail',
                       args=[self.kwargs[self.pk_url_kwarg]])


class PostCreateView(PostsEditMixin, LoginRequiredMixin, CreateView):
    model = Post
    form_class = CreatePostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse(
            'blog:profile',
            args=[self.request.user.username]
        )


class CommentCreateView(CommentEditMixin, LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CreateCommentForm

    def form_valid(self, form):
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        form.instance.author = self.request.user
        return super().form_valid(form)


class CommentDeleteView(CommentEditMixin, LoginRequiredMixin, DeleteView):
    model = Comment
    pk_url_kwarg = 'comment_id'

    def delete(self, request, *args, **kwargs):
        comment = get_object_or_404(Comment, pk=self.kwargs[self.pk_url_kwarg])
        if self.request.user != comment.author:
            return redirect('blog:post_detail', post_id=self.kwargs['post_id'])
        return super().delete(request, *args, **kwargs)


class CommentUpdateView(CommentEditMixin, LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CreateCommentForm
    pk_url_kwarg = 'comment_id'

    def dispatch(self, request, *args, **kwargs):
        comment = get_object_or_404(Comment, pk=self.kwargs[self.pk_url_kwarg])
        if self.request.user != comment.author:
            return redirect('blog:post_detail', post_id=self.kwargs['post_id'])

        return super().dispatch(request, *args, **kwargs)


class AuthorProfileListView(PostsQuerySetMixin, ListView):
    model = Post
    template_name = 'blog/profile.html'
    paginate_by = PAGINATED_BY

    def get_queryset(self):
        queryset = super().get_queryset()
        author = get_object_or_404(User, username=self.kwargs['username'])
        if self.request.user == author:
            queryset = author.posts.all()
        else:
            queryset = queryset.filter(author=author, is_published=True)
        return self.add_comment_count_annotation(queryset)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(
            User, username=self.kwargs['username']
        )
        return context


class BlogIndexListView(PostsQuerySetMixin, ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    paginate_by = PAGINATED_BY

    queryset_filter = {'category__is_published': True}

    def get_queryset(self):
        return super().get_queryset().filter(**self.queryset_filter)


class BlogCategoryListView(PostsQuerySetMixin, ListView):
    model = Post
    template_name = 'blog/category.html'
    context_object_name = 'post_list'
    paginate_by = PAGINATED_BY

    def get_queryset(self):
        category_slug = self.kwargs['category_slug']
        self.category = self.get_category(category_slug)
        queryset = super().get_queryset().filter(category__slug=category_slug,
                                                 is_published=True)
        return self.add_comment_count_annotation(queryset)

    def get_category(self, category_slug):
        return get_object_or_404(Category, slug=category_slug,
                                 is_published=True)


class PostDetailView(PostsQuerySetMixin, DetailView):
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CreateCommentForm()
        context['comments'] = (
            self.get_object().comments.prefetch_related('author').all()
        )
        return context

    def get_object(self, queryset=None):
        post = get_object_or_404(Post, pk=self.kwargs.get(self.pk_url_kwarg))
        if self.request.user == post.author:
            return post
        return get_object_or_404(Post, pk=self.kwargs.get(self.pk_url_kwarg),
                                 is_published=True)

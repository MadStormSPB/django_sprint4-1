from django.db.models import Count
from django.urls import reverse
from django.db import models
from django.utils import timezone

from .models import Comment, Post


class PostsQuerySetMixin:
    def filter_published_posts(self, queryset):
        return queryset.filter(
            is_published=True,
            pub_date__lte=timezone.now()
        )

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = self.filter_published_posts(queryset)
        queryset = self.add_comment_count_annotation(queryset)
        return queryset

    def add_comment_count_annotation(self, queryset):
        return queryset.annotate(comment_count=Count
                                 ('comments')).select_related(
            'category',
            'author',
            'location'
        ).order_by('-pub_date')


class PostQuerySet(PostsQuerySetMixin, models.QuerySet):
    pass


class PostsEditMixin:
    model = Post
    template_name = 'blog/create.html'


class CommentEditMixin:
    model = Comment
    pk_url_kwarg = 'comment_pk'
    template_name = 'blog/comment.html'

    def get_success_url(self):
        return reverse('blog:post_detail', args=[self.kwargs['post_id']])

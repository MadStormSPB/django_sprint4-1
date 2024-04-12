from django.utils import timezone
from .models import Comment, Post
from django.db.models import Count
from django.urls import reverse


class PostsQuerySetMixin:
    def get_queryset(self):
        queryset = Post.objects.filter(
            is_published=True,
            pub_date__lte=timezone.now()
        )
        if hasattr(self, 'category_slug'):
            queryset = queryset.filter(category__slug=self.category_slug)
        return queryset

    def add_comment_count_annotation(self, queryset):
        return (queryset.annotate(comment_count=Count('comments')).order_by
                ('-pub_date').select_related(
            'category',
            'author',
            'location'
        ))


class PostsEditMixin:
    model = Post
    template_name = 'blog/create.html'


class CommentEditMixin:
    model = Comment
    pk_url_kwarg = 'comment_pk'
    template_name = 'blog/comment.html'

    def get_success_url(self):
        return reverse('blog:post_detail', args=[self.kwargs['post_id']])

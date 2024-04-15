from django.db.models import Count
from django.urls import reverse
from django.utils import timezone

from .models import Comment, Post


def filter_published_posts(posts_queryset):
    return posts_queryset.filter(
        is_published=True,
        pub_date__lte=timezone.now()
    )


def add_comment_count_annotation(posts_queryset):
    return (posts_queryset.annotate(comment_count=Count('comments'))
            .order_by('-pub_date')
            .select_related('category', 'author', 'location'))


def get_posts_queryset():
    queryset = Post.objects.all()
    queryset = filter_published_posts(queryset)
    queryset = add_comment_count_annotation(queryset)
    return queryset


class PostsEditMixin:
    model = Post
    template_name = 'blog/create.html'


class CommentEditMixin:
    model = Comment
    pk_url_kwarg = 'comment_pk'
    template_name = 'blog/comment.html'

    def get_success_url(self):
        return reverse('blog:post_detail', args=[self.kwargs['post_id']])

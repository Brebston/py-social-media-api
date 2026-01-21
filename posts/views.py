from django.db.models import Count
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from accounts.permissions import IsOwnerOrReadOnly
from accounts.models import Follow
from interactions.models import Like
from .models import Post
from .serializers import PostReadSerializer, PostCreateUpdateSerializer


class PostViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        following_ids = Follow.objects.filter(follower=user).values_list(
            "following_id", flat=True
        )

        qs = (
            Post.objects.select_related("author")
            .prefetch_related("hashtags")
            .filter(status=Post.Status.PUBLISHED)
            .filter(author_id__in=list(following_ids) + [user.id])
            .annotate(
                likes_count=Count("likes", distinct=True),
                comments_count=Count("comments", distinct=True),
            )
        )

        hashtag = self.request.query_params.get("hashtag")
        if hashtag:
            qs = qs.filter(hashtags__name=hashtag.lower())

        author_id = self.request.query_params.get("author")
        if author_id:
            qs = qs.filter(author_id=author_id)

        return qs

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return PostReadSerializer
        return PostCreateUpdateSerializer

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        post = self.get_object()
        Like.objects.get_or_create(user=request.user, post=post)
        return Response({"detail": "Liked"}, status=status.HTTP_201_CREATED)

    @like.mapping.delete
    def unlike(self, request, pk=None):
        Like.objects.filter(user=request.user, post_id=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"])
    def my_posts(self, request):
        qs = (
            Post.objects.select_related("author")
            .prefetch_related("hashtags")
            .filter(author=request.user)
            .annotate(
                likes_count=Count("likes", distinct=True),
                _toggle_comments_count=Count("comments", distinct=True),
                comments_count=Count("comments", distinct=True),
            )
            .order_by("-created_at")
        )
        page = self.paginate_queryset(qs)
        if page is not None:
            ser = PostReadSerializer(page, many=True)
            return self.get_paginated_response(ser.data)
        return Response(PostReadSerializer(qs, many=True).data)

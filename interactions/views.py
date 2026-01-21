from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from accounts.permissions import IsOwnerOrReadOnly
from posts.models import Post
from .models import Like, Comment
from .serializers import CommentReadSerializer, CommentCreateSerializer


class LikeViewSet(viewsets.ViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=["post"], url_path="like", url_name="like")
    def like(self, request, pk=None):
        post = get_object_or_404(Post, pk=pk)
        Like.objects.get_or_create(user=request.user, post=post)
        return Response({"detail": "Liked"}, status=status.HTTP_201_CREATED)

    @like.mapping.delete
    def unlike(self, request, pk=None):
        Like.objects.filter(user=request.user, post_id=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"], url_path="me/liked-posts")
    def my_liked_posts(self, request):
        post_ids = Like.objects.filter(user=request.user).values_list(
            "post_id", flat=True
        )
        return Response({"post_ids": list(post_ids)})


class CommentViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        qs = Comment.objects.select_related("author", "post").all()
        post_id = self.request.query_params.get("post")
        if post_id:
            qs = qs.filter(post_id=post_id)
        return qs.order_by("created_at")

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return CommentReadSerializer
        return CommentCreateSerializer

    def perform_create(self, serializer):
        post_id = self.request.data.get("post")
        if not post_id:
            raise ValidationError({"post": "This field is required."})
        # Ensure post exists.
        get_object_or_404(Post, pk=post_id)
        serializer.save(author=self.request.user, post_id=post_id)

    @action(detail=False, methods=["post"], url_path=r"posts/(?P<post_id>\d+)/comments")
    def add_to_post(self, request, post_id=None):
        ser = CommentCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        comment = ser.save(author=request.user, post_id=post_id)
        return Response(
            CommentReadSerializer(comment).data, status=status.HTTP_201_CREATED
        )

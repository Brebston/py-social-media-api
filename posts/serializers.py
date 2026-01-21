import re
from rest_framework import serializers
from django.contrib.auth import get_user_model

from posts.models import Post, Hashtag

User = get_user_model()
HASHTAG_RE = re.compile(r"#(?P<tag>[a-zA-Z0-9_]{1,50})")


class HashtagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hashtag
        fields = ("name",)


class PostReadSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    hashtags = serializers.SlugRelatedField(
        slug_field="name", read_only=True, many=True
    )
    likes_count = serializers.IntegerField(read_only=True)
    comments_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Post
        fields = (
            "id",
            "author",
            "content",
            "hashtags",
            "status",
            "scheduled_for",
            "created_at",
            "updated_at",
            "likes_count",
            "comments_count",
        )

    def get_author(self, obj):
        return {"id": obj.author_id, "username": getattr(obj.author, "username", None)}


class PostCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ("content", "scheduled_for")

    def validate(self, attrs):
        content = attrs.get("content")
        if content is not None and not content.strip():
            raise serializers.ValidationError({"content": "Content cannot be empty."})
        return attrs

    def _sync_hashtags(self, post: Post):
        tags = set(t.lower() for t in HASHTAG_RE.findall(post.content or ""))
        objs = []
        for t in tags:
            obj, _ = Hashtag.objects.get_or_create(name=t)
            objs.append(obj)
        post.hashtags.set(objs)

    def create(self, validated_data):
        request = self.context["request"]
        scheduled_for = validated_data.get("scheduled_for")

        post = Post.objects.create(
            author=request.user,
            status=Post.Status.SCHEDULED if scheduled_for else Post.Status.PUBLISHED,
            **validated_data,
        )
        self._sync_hashtags(post)
        return post

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        if "content" in validated_data:
            self._sync_hashtags(instance)
        return instance
